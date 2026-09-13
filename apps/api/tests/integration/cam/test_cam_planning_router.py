from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_ingestion_gateway
from app.modules.cad.ingestion import CadIngestionGateway
from app.modules.cad.ingestion_schemas import (
    CadProfileBoundingBox,
    CadProfileData,
    CadProfilePoint,
)


TURNING_FIXTURES = Path(__file__).parents[2] / "fixtures" / "cad" / "turning"
VALID_STEP = (TURNING_FIXTURES / "cylinder_d50_l100.stp").read_bytes()


def _install_gateway(root: Path) -> CadIngestionGateway:
    gateway = CadIngestionGateway(root)
    app.dependency_overrides[get_cad_ingestion_gateway] = lambda: gateway
    return gateway


def _remove_gateway(gateway: CadIngestionGateway) -> None:
    app.dependency_overrides.pop(get_cad_ingestion_gateway, None)
    gateway.close()


def _dispatch(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/cad/step/dispatch",
        headers=headers,
        files={"file": ("fixture.step", VALID_STEP, "application/step")},
    )
    assert response.status_code == 202, response.text
    return str(response.json()["job_id"])


def _plan_payload(job_id: str) -> dict[str, object]:
    return {
        "cad_job_id": job_id,
        "operation_type": "FACING",
        "tool_params": {
            "tip_radius_mm": 0.8,
            "cutting_edge_angle_deg": 95.0,
            "cutting_edge_length_mm": 12.0,
            "orientation": "RIGHT_HAND",
            "compensation": "NONE",
        },
        "cutting_params": {
            "vc_m_per_min": 180.0,
            "feed_mm_per_rev": 0.2,
            "depth_of_cut_mm": 0.5,
        },
        "linear_tolerance_mm": 0.001,
        "material_reference": "AISI 1020 reference only",
        "stock_radius_mm": 26.0,
        "stock_front_z_mm": 1.0,
        "target_front_z_mm": 0.0,
        "finish_allowance_mm": 0.0,
    }


def test_plans_authenticated_turning_strategy_from_completed_cad_profile(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cam-planning-owner@vena-ia.dev")
        job_id = _dispatch(client, account.headers)

        response = client.post(
            "/api/v1/cam/turning/plan",
            headers=account.headers,
            json=_plan_payload(job_id),
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["cad_job_id"] == job_id
        assert body["plan_id"]
        assert body["status"] == "PLANNED_REQUIRES_REVIEW"
        assert body["operation_type"] == "FACING"
        assert body["passes"]
        assert body["executable_output"] is False
        assert body["physical_use_authorized"] is False
        assert body["g9_status"] == "PENDING_AUTHORITATIVE_REVIEW"
        assert body["emission_status"] == "CONTROLLER_PROFILE_UNRESOLVED"
    finally:
        _remove_gateway(gateway)


def test_rejects_cad_job_without_reviewable_profile(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cam-planning-pending@vena-ia.dev")
        job_id = _dispatch(client, account.headers)
        gateway.mark_failed(job_id, "STEP_PROFILE_EXTRACTION_FAILED")

        response = client.post(
            "/api/v1/cam/turning/plan",
            headers=account.headers,
            json=_plan_payload(job_id),
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "CAD_JOB_PROFILE_NOT_REVIEWABLE"
    finally:
        _remove_gateway(gateway)


def test_rejects_degenerate_completed_profile_fail_closed(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cam-planning-degenerate@vena-ia.dev")
        job_id = _dispatch(client, account.headers)
        gateway.mark_completed(
            job_id,
            CadProfileData(
                points=(
                    CadProfilePoint(r_mm=0.0, z_mm=0.0),
                    CadProfilePoint(r_mm=10.0, z_mm=0.0),
                    CadProfilePoint(r_mm=9.0, z_mm=-20.0),
                    CadProfilePoint(r_mm=0.0, z_mm=-20.0),
                ),
                bounding_box=CadProfileBoundingBox(
                    max_radius_mm=25.0,
                    min_z_mm=-20.0,
                    max_z_mm=0.0,
                    total_z_length_mm=20.0,
                ),
                review_status="PROFILE_AVAILABLE_REQUIRES_REVIEW",
            ),
        )

        response = client.post(
            "/api/v1/cam/turning/plan",
            headers=account.headers,
            json=_plan_payload(job_id),
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "PROFILE_BOUNDING_RADIUS_MISMATCH"
    finally:
        _remove_gateway(gateway)


def test_turning_plan_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cam/turning/plan",
        json=_plan_payload("untrusted-job"),
    )

    assert response.status_code == 401
