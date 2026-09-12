from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_ingestion_gateway
from app.modules.cad.ingestion import CadIngestionGateway


VALID_STEP = b"""ISO-10303-21;
HEADER;
FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF'));
ENDSEC;
DATA;
ENDSEC;
END-ISO-10303-21;
"""


def _install_gateway(root: Path, *, max_size_bytes: int = 15 * 1024 * 1024):
    gateway = CadIngestionGateway(root, max_size_bytes=max_size_bytes)
    app.dependency_overrides[get_cad_ingestion_gateway] = lambda: gateway
    return gateway


def _remove_gateway(gateway: CadIngestionGateway) -> None:
    app.dependency_overrides.pop(get_cad_ingestion_gateway, None)
    gateway.close()


def test_dispatches_valid_step_to_owner_scoped_sandbox(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cad-gateway-owner@vena-ia.dev")
        response = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("fixture.STEP", VALID_STEP, "application/step")},
        )

        assert response.status_code == 202, response.text
        body = response.json()
        assert body == {
            "job_id": body["job_id"],
            "filename": "fixture.STEP",
            "size_bytes": len(VALID_STEP),
            "schema_type": "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF",
            "status": "QUEUED",
        }
        persisted = list(tmp_path.glob("*.step"))
        assert len(persisted) == 1
        assert persisted[0].read_bytes() == VALID_STEP

        job_response = client.get(
            f"/api/v1/cad/step/jobs/{body['job_id']}",
            headers=account.headers,
        )
        assert job_response.status_code == 200
        assert job_response.json() == {
            "job_id": body["job_id"],
            "status": "QUEUED",
            "error_detail": None,
        }

        outsider = make_account("cad-gateway-outsider@vena-ia.dev")
        hidden_job = client.get(
            f"/api/v1/cad/step/jobs/{body['job_id']}",
            headers=outsider.headers,
        )
        assert hidden_job.status_code == 404
    finally:
        _remove_gateway(gateway)


def test_rejects_invalid_extension_before_persistence(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cad-invalid-extension@vena-ia.dev")
        response = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("fixture.stl", VALID_STEP, "application/octet-stream")},
        )
        assert response.status_code == 400
        assert list(tmp_path.iterdir()) == []
    finally:
        _remove_gateway(gateway)


def test_rejects_missing_signature_and_oversized_payload_without_residue(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path, max_size_bytes=64)
    try:
        account = make_account("cad-invalid-content@vena-ia.dev")
        missing_signature = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("masked.step", b"not a STEP payload", "application/step")},
        )
        oversized = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("large.stp", VALID_STEP, "application/step")},
        )

        assert missing_signature.status_code == 422
        assert oversized.status_code == 422
        assert list(tmp_path.iterdir()) == []
    finally:
        _remove_gateway(gateway)


def test_dispatch_requires_authentication(client: TestClient, tmp_path: Path) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        response = client.post(
            "/api/v1/cad/step/dispatch",
            files={"file": ("fixture.step", VALID_STEP, "application/step")},
        )
        assert response.status_code == 401
        assert list(tmp_path.iterdir()) == []
    finally:
        _remove_gateway(gateway)
