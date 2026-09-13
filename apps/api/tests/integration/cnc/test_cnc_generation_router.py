from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_ingestion_gateway
from app.modules.cad.ingestion import CadIngestionGateway


TURNING_FIXTURES = Path(__file__).parents[2] / "fixtures" / "cad" / "turning"
VALID_STEP = (TURNING_FIXTURES / "cylinder_d50_l100.stp").read_bytes()


def _install_gateway(root: Path) -> CadIngestionGateway:
    gateway = CadIngestionGateway(root)
    app.dependency_overrides[get_cad_ingestion_gateway] = lambda: gateway
    return gateway


def _remove_gateway(gateway: CadIngestionGateway) -> None:
    app.dependency_overrides.pop(get_cad_ingestion_gateway, None)
    gateway.close()


def _create_plan(client: TestClient, headers: dict[str, str]) -> str:
    dispatch = client.post(
        "/api/v1/cad/step/dispatch",
        headers=headers,
        files={"file": ("fixture.step", VALID_STEP, "application/step")},
    )
    assert dispatch.status_code == 202, dispatch.text
    response = client.post(
        "/api/v1/cam/turning/plan",
        headers=headers,
        json={
            "cad_job_id": dispatch.json()["job_id"],
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
        },
    )
    assert response.status_code == 200, response.text
    return str(response.json()["plan_id"])


def _generation_payload(plan_id: str) -> dict[str, object]:
    return {
        "plan_id": plan_id,
        "controller_profile": "SIMULATED_STUB",
        "program_number": 9002,
    }


def test_generates_review_only_candidate_from_owned_cam_plan(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cnc-generation-owner@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=account.headers,
            json=_generation_payload(plan_id),
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["plan_id"] == plan_id
        assert body["status"] == "PLANNED_REQUIRES_REVIEW"
        assert body["program_text"].startswith("O9002")
        assert "G21\nG18\nG95\nG96 S180" in body["program_text"]
        assert body["safety_level"] == "AUDIT_ONLY_NON_EXECUTABLE"
        assert body["safety_flags"]["executable_output"] is False
        assert body["safety_flags"]["physical_use_authorized"] is False
    finally:
        _remove_gateway(gateway)


def test_generation_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cnc/turning/generate",
        json=_generation_payload("untrusted-plan"),
    )

    assert response.status_code == 401


def test_generation_hides_plan_from_another_owner(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        owner = make_account("cnc-plan-owner@vena-ia.dev")
        outsider = make_account("cnc-plan-outsider@vena-ia.dev")
        plan_id = _create_plan(client, owner.headers)

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=outsider.headers,
            json=_generation_payload(plan_id),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "CAM turning plan not found"
    finally:
        _remove_gateway(gateway)


def test_generation_rejects_unsupported_controller_profile(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cnc-invalid-controller@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)
        payload = _generation_payload(plan_id)
        payload["controller_profile"] = "UNCONFIGURED_CONTROLLER"

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=account.headers,
            json=payload,
        )

        assert response.status_code == 422
    finally:
        _remove_gateway(gateway)


@pytest.mark.parametrize(
    ("controller_profile", "expected_tokens"),
    (
        ("FANUC_0I", ("O9002", "T0101", "G50 S3000", "G96 S180")),
        (
            "SIEMENS_840D",
            ("%_N_VENA_9002_MPF", 'T="FERRAMENTA" D1', "LIMS=3000", "G0 X"),
        ),
        ("HAAS", ("O9002", "T0101", "G50 S3000", "M30\n%")),
    ),
)
def test_gateway_generates_selected_controller_dialect(
    client: TestClient,
    make_account,
    tmp_path: Path,
    controller_profile: str,
    expected_tokens: tuple[str, ...],
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account(f"cnc-dialect-{controller_profile.lower()}@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)
        payload = _generation_payload(plan_id)
        payload["controller_profile"] = controller_profile

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=account.headers,
            json=payload,
        )

        assert response.status_code == 200, response.text
        program = response.json()["program_text"]
        assert all(token in program for token in expected_tokens)
        assert "PHYSICAL_USE_AUTHORIZED=FALSE" in program
        assert response.json()["safety_flags"]["executable_output"] is False
    finally:
        _remove_gateway(gateway)


@pytest.mark.parametrize(
    ("limit_name", "limit_value"),
    (("max_spindle_rpm", 0), ("max_feed_mm_min", 1)),
)
def test_gateway_rejects_invalid_or_incompatible_machine_limits(
    client: TestClient,
    make_account,
    tmp_path: Path,
    limit_name: str,
    limit_value: float,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account(f"cnc-limit-{limit_name}@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)
        payload = _generation_payload(plan_id)
        payload["controller_profile"] = "FANUC_0I"
        payload[limit_name] = limit_value

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=account.headers,
            json=payload,
        )

        assert response.status_code == 422
    finally:
        _remove_gateway(gateway)
