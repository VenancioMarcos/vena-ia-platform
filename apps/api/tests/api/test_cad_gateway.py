from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_ingestion_gateway
from app.modules.cad.ingestion import CadIngestionGateway


INVALID_GEOMETRY_STEP = b"""ISO-10303-21;
HEADER;
FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF'));
ENDSEC;
DATA;
ENDSEC;
END-ISO-10303-21;
"""
TURNING_FIXTURES = Path(__file__).parents[1] / "fixtures" / "cad" / "turning"
VALID_STEP = (TURNING_FIXTURES / "cylinder_d50_l100.stp").read_bytes()


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
            "schema_type": body["schema_type"],
            "status": "QUEUED",
        }
        assert list(tmp_path.iterdir()) == []

        job_response = client.get(
            f"/api/v1/cad/step/jobs/{body['job_id']}",
            headers=account.headers,
        )
        assert job_response.status_code == 200
        assert job_response.json() == {
            "job_id": body["job_id"],
            "status": "COMPLETED",
            "error_detail": None,
            "profile_data": {
                "points": [
                    {"r_mm": 0.0, "z_mm": 0.0},
                    {"r_mm": 25.0, "z_mm": 0.0},
                    {"r_mm": 25.0, "z_mm": -100.0},
                    {"r_mm": 0.0, "z_mm": -100.0},
                ],
                "warnings": [],
                "bounding_box": {
                    "max_radius_mm": 25.0,
                    "min_z_mm": -100.0,
                    "max_z_mm": 0.0,
                    "total_z_length_mm": 100.0,
                },
                "review_status": "PROFILE_AVAILABLE_REQUIRES_REVIEW",
            },
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


def test_corrupt_geometry_fails_without_internal_details_or_sandbox_residue(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cad-corrupt-geometry@vena-ia.dev")
        response = client.post(
            "/api/v1/cad/step/dispatch",
            headers=account.headers,
            files={"file": ("corrupt.step", INVALID_GEOMETRY_STEP, "application/step")},
        )
        assert response.status_code == 202

        status_response = client.get(
            f"/api/v1/cad/step/jobs/{response.json()['job_id']}",
            headers=account.headers,
        )
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "FAILED"
        assert status_response.json()["error_detail"] == "STEP_PROFILE_EXTRACTION_FAILED"
        assert status_response.json()["profile_data"] is None
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
