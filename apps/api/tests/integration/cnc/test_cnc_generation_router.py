from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_ingestion_gateway
from app.modules.cad.ingestion import CadIngestionGateway
from app.modules.cam.schemas import RzPoint, TurningBoundingBox


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
        "machine_envelope": {
            "x_min_mm": 0.0,
            "x_max_mm": 100.0,
            "z_min_mm": -200.0,
            "z_max_mm": 200.0,
            "chuck_exclusion_zone": {
                "x_min_mm": 0.0,
                "x_max_mm": 100.0,
                "z_min_mm": 50.0,
                "z_max_mm": 100.0,
            },
        },
    }


def _simulation_geometry() -> dict[str, object]:
    return {
        "machine_envelope": _generation_payload("unused")["machine_envelope"],
        "stock": {
            "diameter_mm": 52.0,
            "z_min_mm": -100.0,
            "z_max_mm": 1.0,
        },
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


def test_gateway_rejects_chuck_zone_collision_as_unprocessable(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cnc-envelope-collision@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)
        payload = _generation_payload(plan_id)
        payload["controller_profile"] = "FANUC_0I"
        payload["machine_envelope"] = {
            "x_min_mm": 0.0,
            "x_max_mm": 100.0,
            "z_min_mm": -200.0,
            "z_max_mm": 200.0,
            "chuck_exclusion_zone": {
                "x_min_mm": 40.0,
                "x_max_mm": 60.0,
                "z_min_mm": -1.0,
                "z_max_mm": 2.0,
            },
        }

        response = client.post(
            "/api/v1/cnc/turning/generate",
            headers=account.headers,
            json=payload,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "CHUCK_EXCLUSION_ZONE_VIOLATION"
    finally:
        _remove_gateway(gateway)


def test_simulation_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cnc/turning/simulate-toolpath",
        json={
            "program_text": "G00 X40 Z2\nG01 X36 Z-20 F0.2",
            "controller_profile": "FANUC_0I",
            **_simulation_geometry(),
        },
    )

    assert response.status_code == 401


def test_simulation_endpoint_returns_safe_payload_from_owned_plan(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        account = make_account("cnc-simulation-owner@vena-ia.dev")
        plan_id = _create_plan(client, account.headers)

        response = client.post(
            "/api/v1/cnc/turning/simulate-toolpath",
            headers=account.headers,
            json={
                "plan_id": plan_id,
                "controller_profile": "FANUC_0I",
                "program_number": 9003,
                **_simulation_geometry(),
            },
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["source_plan_id"] == plan_id
        assert body["status"] == "SIMULATION_READY_REQUIRES_REVIEW"
        assert body["segments"]
        assert body["segments"][0]["active_tool"] == "T0101"
        assert body["chuck_proximity"]["minimum_clearance_mm"] >= 0
        assert body["chuck_proximity"]["threshold_mm"] == 5.0
        assert body["chuck_proximity"]["closest_segment_index"] >= 0
        assert body["chuck_proximity"]["warning_code"] in (
            None,
            "WARNING_PROXIMITY_CHUCK",
        )
        assert body["safety_flags"]["machine_send"] is False
        assert body["safety_flags"]["executable_output"] is False
    finally:
        _remove_gateway(gateway)


def test_report_requires_owned_plan_and_completed_plan_simulation(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        owner = make_account("cnc-report-owner@vena-ia.dev")
        outsider = make_account("cnc-report-outsider@vena-ia.dev")
        plan_id = _create_plan(client, owner.headers)
        endpoint = f"/api/v1/cnc/turning/plans/{plan_id}/report"

        assert client.get(endpoint).status_code == 401
        assert client.get(endpoint, headers=owner.headers).status_code == 422
        assert client.get(endpoint, headers=outsider.headers).status_code == 404

        simulated = client.post(
            "/api/v1/cnc/turning/simulate-toolpath",
            headers=owner.headers,
            json={
                "plan_id": plan_id,
                "controller_profile": "FANUC_0I",
                "program_number": 9004,
                **_simulation_geometry(),
            },
        )
        assert simulated.status_code == 200, simulated.text

        response = client.get(endpoint, headers=owner.headers)
        assert response.status_code == 422, response.text
        body = response.json()
        assert body["detail"]["code"] == "GEOMETRY_DIMENSIONAL_AUDIT_REJECTED"
        audit = body["detail"]["audit"]
        assert audit["schema_version"] == "vena-ia.cnc-geometry-dimensional-audit/v1"
        assert audit["status"] == "REJECTED"
        assert audit["manifest_generation_allowed"] is False
        assert "BREP_MAX_RADIUS_MISMATCH" in audit["findings"]
        assert "BREP_MIN_Z_MISMATCH" in audit["findings"]
        assert audit["safety_flags"]["physical_use_authorized"] is False
        assert audit["safety_flags"]["executable_output"] is False
        assert "program_text" not in body
        assert client.get(endpoint, headers=outsider.headers).status_code == 404
    finally:
        _remove_gateway(gateway)


def test_download_report_requires_approved_dimensional_audit_and_owner(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    gateway = _install_gateway(tmp_path)
    try:
        owner = make_account("cnc-download-owner@vena-ia.dev")
        outsider = make_account("cnc-download-outsider@vena-ia.dev")
        plan_id = _create_plan(client, owner.headers)
        store = app.state.turning_plan_store
        record = store.get_owned(plan_id, owner_user_id=owner.id)
        store.save(
            owner_user_id=owner.id,
            request=record.request,
            response=record.response,
            source_brep_bounds=TurningBoundingBox(
                max_radius_mm=26.0,
                min_z_mm=0.0,
                max_z_mm=0.5,
                total_z_length_mm=0.5,
            ),
            source_profile_data=(
                RzPoint(r_mm=0.0, z_mm=0.5),
                RzPoint(r_mm=26.0, z_mm=0.5),
                RzPoint(r_mm=26.0, z_mm=0.0),
                RzPoint(r_mm=0.0, z_mm=0.0),
            ),
        )
        endpoint = f"/api/v1/cnc/turning/plans/{plan_id}/report/download"

        assert client.get(endpoint).status_code == 401
        assert client.get(endpoint, headers=owner.headers).status_code == 422
        assert client.get(endpoint, headers=outsider.headers).status_code == 404
        simulated = client.post(
            "/api/v1/cnc/turning/simulate-toolpath",
            headers=owner.headers,
            json={
                "plan_id": plan_id,
                "controller_profile": "FANUC_0I",
                "program_number": 9005,
                **_simulation_geometry(),
            },
        )
        assert simulated.status_code == 200, simulated.text

        response = client.get(endpoint, headers=owner.headers)
        assert response.status_code == 200, response.text
        assert response.headers["content-type"].startswith("text/plain")
        assert response.headers["content-disposition"].startswith("attachment;")
        assert response.headers["cache-control"] == "no-store, private"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["content-security-policy"] == "default-src 'none'; sandbox"
        assert response.text.count(
            "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO"
        ) == 13
        assert "[ENVELOPE DE POTÊNCIA E TORQUE DO FUSO]" in response.text
        assert "power_margin_percent=" in response.text
        assert "[EXPANSÃO TÉRMICA E DERIVA DE EIXOS]" in response.text
        assert "[DESGASTE GEOMÉTRICO DA FERRAMENTA]" in response.text
        assert "radial_deviation_um=" in response.text
        assert "[FORMAÇÃO E QUEBRA DE CAVACO]" in response.text
        assert "chipbreaker_reference=CNMG_120408_PM_TABULATED" in response.text
        assert (
            "ESTIMATIVA ANALÍTICA DE FORMAÇÃO E QUEBRA DE CAVACO - NÃO CONSIDERA "
            "FLUTUAÇÕES DINÂMICAS DE PRESSÃO DE REFRIGERAÇÃO OU VARIAÇÕES "
            "MICROESTRUTURAIS" in response.text
        )
        assert "[DEMANDA DE FLUIDO POR ZONA TÉRMICA]" in response.text
        assert "zone[SECONDARY_TOOL_CHIP_INTERFACE]" in response.text
        assert "status=COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS" in response.text
        assert (
            "ESTIMATIVA ANALÍTICA DE DEMANDA DE FLUIDO - NÃO CONTROLA BOMBAS OU "
            "VÁLVULAS DE MÁQUINA" in response.text
        )
        assert "[FLEXÃO ELÁSTICA DA PEÇA]" in response.text
        assert (
            "ESTIMATIVA ANALÍTICA DE FLEXÃO ELÁSTICA DA PEÇA - NÃO CONSIDERA "
            "CONTAPONTO OU LUNETA DE APOIO" in response.text
        )
        assert "[FOLHA DE PROCESSO]" in response.text
        assert "FOLHA DE PROCESSO TEÓRICA ANALÍTICA" in response.text
        assert "[AUDITORIA DE MATERIAL REMANESCENTE]" in response.text
        assert "AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE" in response.text
        assert "status=PASS" in response.text
        assert "program_text" not in response.text
        assert client.get(endpoint, headers=outsider.headers).status_code == 404
    finally:
        _remove_gateway(gateway)
