from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.cad.dependencies import (
    get_cad_ingestion_gateway,
    get_step_background_processor,
)
from app.modules.cad.ingestion import MAX_STEP_UPLOAD_BYTES, CadIngestionGateway
from app.modules.cad.ingestion_schemas import (
    CadProfileBoundingBox,
    CadProfileData,
    CadProfilePoint,
)
from app.modules.cad.parser import StepTextParser


TURNING_FIXTURES = Path(__file__).parents[1] / "fixtures" / "cad" / "turning"
VALID_STEP = (TURNING_FIXTURES / "cylinder_d50_l100.stp").read_bytes()


class BoundedStressProcessor:
    """Complete ingestion jobs without benchmarking OCCT on artificial padding."""

    def __init__(self, gateway: CadIngestionGateway) -> None:
        self._gateway = gateway

    def process(self, job_id: str) -> None:
        try:
            self._gateway.mark_processing(job_id)
            self._gateway.mark_completed(
                job_id,
                CadProfileData(
                    points=(
                        CadProfilePoint(r_mm=0, z_mm=0),
                        CadProfilePoint(r_mm=25, z_mm=0),
                        CadProfilePoint(r_mm=25, z_mm=-100),
                        CadProfilePoint(r_mm=0, z_mm=-100),
                    ),
                    bounding_box=CadProfileBoundingBox(
                        max_radius_mm=25,
                        min_z_mm=-100,
                        max_z_mm=0,
                        total_z_length_mm=100,
                    ),
                    review_status="PROFILE_AVAILABLE_REQUIRES_REVIEW",
                ),
            )
        finally:
            self._gateway.delete_job_file(job_id)


def _install_gateway(root: Path) -> CadIngestionGateway:
    gateway = CadIngestionGateway(root)
    app.dependency_overrides[get_cad_ingestion_gateway] = lambda: gateway
    return gateway


def _remove_gateway(gateway: CadIngestionGateway) -> None:
    app.dependency_overrides.pop(get_cad_ingestion_gateway, None)
    app.dependency_overrides.pop(get_step_background_processor, None)
    app.dependency_overrides.pop(get_current_user, None)
    gateway.close()


def _step_at_upload_limit() -> bytes:
    entity_block = (
        b"\n#900001=CARTESIAN_POINT('',(1.,2.,3.));"
        b"\n#900002=CARTESIAN_POINT('',(4.,5.,6.));"
        b"\n#900003=CARTESIAN_POINT('',(7.,8.,9.));"
    )
    marker = b"\nENDSEC;\nEND-ISO-10303-21;"
    marker_index = VALID_STEP.rfind(marker)
    assert marker_index > 0
    expanded = VALID_STEP[:marker_index] + entity_block + VALID_STEP[marker_index:]
    padding_size = MAX_STEP_UPLOAD_BYTES - len(expanded)
    assert padding_size >= 4
    padding = b"/*" + (b"X" * (padding_size - 4)) + b"*/"
    payload = expanded[:marker_index] + padding + expanded[marker_index:]
    assert len(payload) == MAX_STEP_UPLOAD_BYTES
    return payload


def test_concurrent_owner_uploads_keep_jobs_isolated_and_clean(
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        # The test exercises concurrent CAD dispatch, not the SQLite-backed auth
        # fixture. UUID identities avoid sharing that fixture's single connection
        # across worker threads while retaining owner-scoped endpoint coverage.
        account_headers = [
            {"Authorization": f"Bearer test-cad-load-{uuid4()}"} for _ in range(4)
        ]
        owner_ids = {
            headers["Authorization"]: str(uuid4()) for headers in account_headers
        }

        def concurrent_current_user(request: Request) -> SimpleNamespace:
            return SimpleNamespace(id=owner_ids[request.headers["authorization"]])

        app.dependency_overrides[get_current_user] = concurrent_current_user
        status_client = TestClient(app)

        def dispatch(index: int):
            # TestClient holds request and portal state. A client per worker keeps
            # concurrent requests independent while avoiding an app-lifespan start
            # for every worker. The shared gateway remains the object under test.
            worker_client = TestClient(app)
            try:
                return worker_client.post(
                    "/api/v1/cad/step/dispatch",
                    headers=account_headers[index],
                    files={
                        "file": (
                            f"concurrent-{index}.step",
                            VALID_STEP,
                            "application/step",
                        )
                    },
                )
            finally:
                worker_client.close()

        with ThreadPoolExecutor(max_workers=4) as executor:
            responses = list(executor.map(dispatch, range(4)))

        assert all(response.status_code == 202 for response in responses), [
            response.text for response in responses
        ]
        job_ids = [response.json()["job_id"] for response in responses]
        assert len(set(job_ids)) == len(job_ids)
        assert list(tmp_path.iterdir()) == []

        for index, job_id in enumerate(job_ids):
            owner_status = status_client.get(
                f"/api/v1/cad/step/jobs/{job_id}",
                headers=account_headers[index],
            )
            other_status = status_client.get(
                f"/api/v1/cad/step/jobs/{job_id}",
                headers=account_headers[(index + 1) % len(account_headers)],
            )
            assert owner_status.status_code == 200
            assert owner_status.json()["status"] == "COMPLETED"
            assert owner_status.json()["profile_data"]["review_status"] == (
                "PROFILE_AVAILABLE_REQUIRES_REVIEW"
            )
            assert other_status.status_code == 404
    finally:
        status_client.close()
        _remove_gateway(gateway)


def test_upload_at_15_mib_ceiling_preserves_contract_and_cleans_sandbox(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    app.dependency_overrides[get_step_background_processor] = lambda: BoundedStressProcessor(
        gateway
    )
    try:
        account = make_account("cad-ceiling@vena-ia.dev")
        payload = _step_at_upload_limit()
        parsed = StepTextParser().parse(payload)
        assert parsed.cartesian_point_count >= 3

        response = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("ceiling.step", payload, "application/step")},
        )

        assert response.status_code == 202, response.text
        assert response.json()["size_bytes"] == MAX_STEP_UPLOAD_BYTES
        status = client.get(
            f"/api/v1/cad/step/jobs/{response.json()['job_id']}",
            headers=account.headers,
        )
        assert status.status_code == 200
        assert status.json()["status"] == "COMPLETED"
        assert status.json()["profile_data"]["review_status"] == (
            "PROFILE_AVAILABLE_REQUIRES_REVIEW"
        )
        assert list(tmp_path.iterdir()) == []
    finally:
        _remove_gateway(gateway)
