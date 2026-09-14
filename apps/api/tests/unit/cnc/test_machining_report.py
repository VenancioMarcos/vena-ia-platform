from dataclasses import replace
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.repository import TurningPlanRecord
from app.modules.cam.schemas import (
    MachiningPass,
    RzPoint,
    TurningBoundingBox,
    TurningPlanGatewayRequest,
    TurningPlanGatewayResponse,
    TurningStrategyPlanResponse,
)
from app.modules.cnc.enums import CNCControllerType, SpindleMode
from app.modules.cnc.schemas import (
    GCodeGenerationRequest,
    GCodeSafetyFlags,
    MachiningTechnicalReportPayload,
    ToolpathSimulationRequest,
    TurningStock2D,
)
from app.modules.cnc.services.gcode_formatter import format_gcode_candidate
from app.modules.cnc.services.cost_time_estimator import estimate_machining_cost_time
from app.modules.cnc.services.machining_report import (
    MachiningReportSource,
    compile_machining_report,
    plan_fingerprint,
)
from app.modules.cnc.services.part_deflection_auditor import audit_part_elastic_deflection
from app.modules.cnc.services.sustainability_estimator import estimate_sustainability
from app.modules.cnc.services.stability_auditor import audit_machining_stability
from app.modules.cnc.services.text_report_exporter import (
    SAFETY_STAMP,
    format_machining_report_text,
)


def _request(**updates: object) -> GCodeGenerationRequest:
    plan = TurningStrategyPlanResponse(
        operation_type=TurningOperationType.ROUGH_TURNING,
        passes=(
            MachiningPass(
                sequence=1,
                operation_type=TurningOperationType.ROUGH_TURNING,
                coordinates_rz_mm=(
                    RzPoint(r_mm=12.0, z_mm=2.0),
                    RzPoint(r_mm=10.0, z_mm=2.0),
                    RzPoint(r_mm=10.0, z_mm=-20.0),
                ),
                estimated_removed_volume_mm3=1_000.0,
            ),
        ),
        material_removal_volume_mm3=1_000.0,
        warnings=("ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW",),
    )
    values: dict[str, object] = {
        "plan_id": "plan-test-001",
        "cam_plan_data": plan,
        "controller_profile": CNCControllerType.FANUC_0I,
        "program_number": 9001,
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
        "review_authentication": "AUTHENTICATED_REVIEW_CONTEXT",
    }
    values.update(updates)
    return GCodeGenerationRequest(**values)


def _stock() -> TurningStock2D:
    return TurningStock2D(diameter_mm=52.0, z_min_mm=-100.0, z_max_mm=1.0)


def _source(controller=CNCControllerType.FANUC_0I):
    generation = _request(
        controller_profile=controller,
        spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
        spindle_value=180.0,
    )
    request = TurningPlanGatewayRequest(
        cad_job_id="cad-report",
        operation_type="ROUGH_TURNING",
        tool_params={
            "tip_radius_mm": 0.8,
            "cutting_edge_angle_deg": 95.0,
            "cutting_edge_length_mm": 12.0,
            "orientation": "RIGHT_HAND",
        },
        cutting_params={"vc_m_per_min": 180.0, "feed_mm_per_rev": 0.2, "depth_of_cut_mm": 0.5},
        linear_tolerance_mm=0.001,
        material_reference="Aço ABNT 1045",
        stock_radius_mm=26.0,
        stock_front_z_mm=2.0,
        target_front_z_mm=0.0,
    )
    record = TurningPlanRecord(
        "owner",
        request,
        TurningPlanGatewayResponse(
            **generation.cam_plan_data.model_dump(),
            plan_id=generation.plan_id,
            cad_job_id=request.cad_job_id,
        ),
        TurningBoundingBox(
            max_radius_mm=12.0,
            min_z_mm=-20.0,
            max_z_mm=2.0,
            total_z_length_mm=22.0,
        ),
        (
            RzPoint(r_mm=0.0, z_mm=2.0),
            RzPoint(r_mm=12.0, z_mm=2.0),
            RzPoint(r_mm=10.0, z_mm=2.0),
            RzPoint(r_mm=10.0, z_mm=-20.0),
            RzPoint(r_mm=0.0, z_mm=-20.0),
        ),
    )
    simulation = ToolpathSimulationRequest(
        plan_id=generation.plan_id,
        controller_profile=controller,
        program_number=generation.program_number,
        machine_envelope=generation.machine_envelope,
        stock=_stock(),
    )
    source = MachiningReportSource(
        "owner",
        plan_fingerprint(record),
        simulation,
        format_gcode_candidate(generation).program_text,
        datetime(2026, 9, 13, tzinfo=timezone.utc),
    )
    return record, source


@pytest.mark.parametrize(
    "controller",
    [CNCControllerType.FANUC_0I, CNCControllerType.SIEMENS_840D, CNCControllerType.HAAS],
)
def test_complete_report_replays_deterministically(controller):
    record, source = _source(controller)
    report = compile_machining_report(record, source)
    assert report == compile_machining_report(record, source)
    assert report.controller_profile == controller
    assert report.tools[0].operations == (record.response.operation_type,)
    assert report.total_distance_mm == pytest.approx(26.0)
    assert report.cycle_time_estimate.total_cutting_time_seconds == pytest.approx(26 / 36 * 60)
    assert report.envelope_audit == "PASS_DECLARED_2D_ENVELOPE_ONLY"
    assert report.chuck_proximity.minimum_clearance_mm > 5
    assert report.geometry_audit.status == "PASS"
    assert report.geometry_audit.manifest_generation_allowed is True
    assert report.surface_roughness_audit.ra_theoretical_um == pytest.approx(1.5625)
    assert report.surface_roughness_audit.rz_theoretical_um == pytest.approx(6.25)
    assert (
        report.surface_roughness_audit.compliance_tag
        == "NOMINAL_RA_TOLERANCE_UNAVAILABLE"
    )
    assert report.power_force_audit.material_profile == "ABNT_1045"
    assert report.power_force_audit.fc_nominal_n > 0
    assert report.power_force_audit.pc_cutting_kw > 0
    assert report.power_force_audit.p_motor_est_kw > report.power_force_audit.pc_cutting_kw
    assert report.power_force_audit.mrr_cm3_min == pytest.approx(18.0)
    assert report.power_force_audit.power_status == "POWER_WITHIN_LIMITS"
    assert report.parameter_optimizations[0].tool_id == report.tools[0].tool_id
    assert report.parameter_optimizations[0].optimization_status == "OPTIMAL_TRADE_OFF_FOUND"
    assert report.parameter_optimizations[0].predicted_mrr_cm3_min > 0
    assert report.risk_matrix.risk_level == "LOW_RISK"
    assert report.risk_matrix.overall_risk_score == 0
    assert report.risk_matrix.minimum_chuck_clearance_mm == pytest.approx(
        report.chuck_proximity.minimum_clearance_mm
    )
    assert report.process_sheet.part_id == report.cad_job_id
    assert report.process_sheet.source_plan_id == report.plan_id
    assert report.process_sheet.total_operations_count == 2
    assert report.process_sheet.sequence_operations[0].phase == "SETUP"
    assert report.process_sheet.sequence_operations[1].phase == "ROUGH_TURNING"
    assert report.process_sheet.source_cycle_time_estimate == report.cycle_time_estimate
    assert report.process_sheet.physical_use_authorized is False
    assert report.residual_stock_audit.status == "UNIFORM_ALLOWANCE_COMPLIANT"
    assert report.residual_stock_audit.max_residual_stock_mm == pytest.approx(0)
    assert report.residual_stock_audit.min_residual_stock_mm == pytest.approx(0)
    assert report.residual_stock_audit.gouging_detected is False
    assert report.part_elastic_deflection_audit.radial_cutting_force_n == pytest.approx(
        report.power_force_audit.fc_nominal_n * 0.5
    )
    assert report.part_elastic_deflection_audit.part_unsupported_length_mm == pytest.approx(22)
    assert report.part_elastic_deflection_audit.minimum_diameter_mm == pytest.approx(20)
    assert report.part_elastic_deflection_audit.deflection_status == (
        "ELASTIC_DEFLECTION_COMPLIANT"
    )
    assert report.tool_life_audits[0].tool_id == report.tools[0].tool_id
    assert report.tool_life_audits[0].estimated_tool_life_minutes > 0
    assert report.tool_life_audits[0].tool_life_consumed_percent > 0
    assert report.cost_time_audit.total_cycle_time_minutes > 15
    assert report.cost_time_audit.machine_cost_component > 0
    assert report.cost_time_audit.tooling_wear_cost_component > 0
    assert report.cost_time_audit.currency == "BRL"
    assert report.sustainability_audit.grid_region == "BRASIL_SIN"
    assert report.sustainability_audit.electrical_energy_kwh > 0
    assert report.sustainability_audit.carbon_emission_kg_co2e > 0
    assert report.governance_stamp == "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO"
    assert report.safety_flags == GCodeSafetyFlags()
    assert report.source_plan_name is None
    assert "program_text" not in report.model_dump()
    assert MachiningTechnicalReportPayload.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("corruption", ["empty", "program", "owner", "plan", "flags", "passes"])
def test_corrupted_sources_fail_closed(corruption):
    record, source = _source()
    if corruption == "empty":
        source = replace(source, program_text="")
    elif corruption == "program":
        source = replace(source, program_text=source.program_text.replace("X20", "X22"))
    elif corruption == "owner":
        source = replace(source, owner_user_id="outsider")
    elif corruption == "plan":
        source = replace(source, plan_fingerprint="0" * 64)
    elif corruption == "flags":
        record = replace(
            record, response=record.response.model_copy(update={"executable_output": True})
        )
    else:
        record = replace(record, response=record.response.model_copy(update={"passes": ()}))
    with pytest.raises(ValueError):
        compile_machining_report(record, source)


@pytest.mark.parametrize("flag", list(GCodeSafetyFlags.model_fields))
def test_report_cannot_promote_safety_flags(flag):
    record, source = _source()
    body = compile_machining_report(record, source).model_dump()
    body["safety_flags"][flag] = (
        "APPROVED"
        if isinstance(body["safety_flags"][flag], str)
        else not body["safety_flags"][flag]
    )
    with pytest.raises(ValidationError):
        MachiningTechnicalReportPayload.model_validate(body)


def test_governance_stamp_cannot_be_removed_or_changed():
    record, source = _source()
    body = compile_machining_report(record, source).model_dump()
    body["governance_stamp"] = "APPROVED FOR MACHINE"
    with pytest.raises(ValidationError):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_valid_cost_audit_from_a_different_cycle():
    record, source = _source()
    report = compile_machining_report(record, source)
    other_cycle = report.cycle_time_estimate.model_copy(
        update={
            "total_cutting_time_seconds": report.cycle_time_estimate.total_cutting_time_seconds + 60,
            "total_cycle_time_seconds": report.cycle_time_estimate.total_cycle_time_seconds + 60,
        }
    )
    other_cost = estimate_machining_cost_time(other_cycle, report.tool_life_audits)
    body = report.model_dump()
    body["cost_time_audit"] = other_cost.model_dump()
    with pytest.raises(ValidationError, match="REPORT_COST_TIME_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_valid_sustainability_audit_from_another_power_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    other_audit = estimate_sustainability(
        motor_power_kw=report.power_force_audit.p_motor_est_kw + 1,
        cutting_time_minutes=report.cost_time_audit.cutting_time_minutes,
        total_cycle_time_minutes=report.cost_time_audit.total_cycle_time_minutes,
    )
    body = report.model_dump()
    body["sustainability_audit"] = other_audit.model_dump()
    with pytest.raises(ValidationError, match="REPORT_SUSTAINABILITY_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_valid_stability_audit_from_another_force_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    current = report.stability_audits[0]
    other = audit_machining_stability(
        tool_id=current.tool_id,
        tool_overhang_mm=current.tool_overhang_mm,
        tool_diameter_mm=current.tool_diameter_mm,
        young_modulus_mpa=current.young_modulus_mpa,
        cutting_force_n=current.cutting_force_n + 100,
        specific_cutting_pressure_n_per_mm2=current.specific_cutting_pressure_n_per_mm2,
        frf_real_compliance_mm_per_n=current.frf_real_compliance_mm_per_n,
        depth_of_cut_mm=current.depth_of_cut_mm,
    )
    body = report.model_dump()
    body["stability_audits"] = (other.model_dump(),)
    with pytest.raises(ValidationError, match="REPORT_STABILITY_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_optimization_transplanted_from_another_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    body = report.model_dump()
    body["parameter_optimizations"][0]["machine_power_limit_kw"] = 50.0
    with pytest.raises(ValidationError, match="REPORT_OPTIMIZATION_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_risk_matrix_transplanted_from_another_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    body = report.model_dump()
    body["risk_matrix"]["minimum_chuck_clearance_mm"] = 4.0
    body["risk_matrix"]["chuck_proximity_warning"] = True
    body["risk_matrix"]["dimensional_risk_score"] = 75.0
    body["risk_matrix"]["overall_risk_score"] = 26.25
    body["risk_matrix"]["risk_level"] = "MODERATE_RISK"
    body["risk_matrix"]["mitigation_recommendations"] = (
        "Revisar trajetória, origem e fixação para ampliar a folga em relação à placa.",
    )
    with pytest.raises(ValidationError, match="REPORT_RISK_MATRIX_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_process_sheet_transplanted_from_another_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    body = report.model_dump()
    body["process_sheet"]["part_id"] = "another-cad-job"
    with pytest.raises(ValidationError, match="REPORT_PROCESS_SHEET_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_residual_stock_audit_transplanted_from_another_plan():
    record, source = _source()
    report = compile_machining_report(record, source)
    body = report.model_dump()
    body["residual_stock_audit"]["source_plan_id"] = "another-plan"
    with pytest.raises(ValidationError, match="REPORT_RESIDUAL_STOCK_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_report_rejects_valid_part_deflection_from_another_force_snapshot():
    record, source = _source()
    report = compile_machining_report(record, source)
    current = report.part_elastic_deflection_audit
    other = audit_part_elastic_deflection(
        part_unsupported_length_mm=current.part_unsupported_length_mm,
        minimum_diameter_mm=current.minimum_diameter_mm,
        radial_cutting_force_n=current.radial_cutting_force_n + 100.0,
        young_modulus_mpa=current.young_modulus_mpa,
        radial_tolerance_mm=current.radial_tolerance_mm,
    )
    body = report.model_dump()
    body["part_elastic_deflection_audit"] = other.model_dump()

    with pytest.raises(ValidationError, match="REPORT_PART_DEFLECTION_SOURCE_INCONSISTENT"):
        MachiningTechnicalReportPayload.model_validate(body)


def test_text_export_is_deterministic_and_stamps_every_section():
    record, source = _source()
    report = compile_machining_report(record, source)

    rendered = format_machining_report_text(report)

    assert rendered == format_machining_report_text(report)
    assert rendered.count(SAFETY_STAMP) == 8
    assert rendered.count("[") == 18
    assert "status=PASS" in rendered
    assert "MAX_RADIUS: nominal_mm=" in rendered
    assert "PHYSICAL_USE_AUTHORIZED=FALSE" in rendered
    assert "G9=PENDING_AUTHORITATIVE_REVIEW" in rendered
    assert "NO_HUMAN_REVIEW_BYPASS=TRUE" in rendered
    assert "MACHINE_SEND=false" in rendered
    assert "DNC=false" in rendered
    assert "NC_TRANSFER=false" in rendered
    assert "CYCLE_START=false" in rendered
    assert "emission_status=CONTROLLER_PROFILE_UNRESOLVED" in rendered
    assert "executable_output=false" in rendered
    assert "program_text" not in rendered
    assert "cutting_force_nominal_n=" in rendered
    assert "power_status=POWER_WITHIN_LIMITS" in rendered
    assert (
        "ESTIMATIVA ENERGÉTICA ANALÍTICA DE KIENZLE - NÃO CONSIDERA "
        "RENDIMENTO DINÂMICO REAL" in rendered
    )
    assert "tool_life[T0101]" in rendered
    assert "ESTIMATIVA ANALÍTICA DE TAYLOR" in rendered
    assert "cost_time: total_minutes=" in rendered
    assert "ESTIMATIVA ECONÔMICA E DE TEMPO ANALÍTICA" in rendered
    assert "sustainability: electrical_energy_kwh=" in rendered
    assert "ESTIMATIVA ECOLÓGICA E ENERGÉTICA ANALÍTICA" in rendered
    assert "stability[T0101]: overhang_ratio_l_d=" in rendered
    assert "status=DYNAMICALLY_STABLE" in rendered
    assert "ESTIMATIVA ANALÍTICA DE ESTABILIDADE DINÂMICA" in rendered
    assert "parameter_optimization[T0101]" in rendered
    assert "status=OPTIMAL_TRADE_OFF_FOUND" in rendered
    assert "SUGESTÃO ANALÍTICA DE PARÂMETROS DE CORTE" in rendered
    assert "risk_matrix: overall_score=0.000000000; risk_level=LOW_RISK" in rendered
    assert "risk_mitigation[1]=Manter revisão humana" in rendered
    assert "MATRIZ DE RISCO ANALÍTICA CONSOLIDADA" in rendered
    assert "[FOLHA DE PROCESSO]" in rendered
    assert "operation[1]: id=OP010; phase=SETUP" in rendered
    assert "operation[2]: id=OP020; phase=ROUGH_TURNING" in rendered
    assert "FOLHA DE PROCESSO TEÓRICA ANALÍTICA" in rendered
    assert "[AUDITORIA DE MATERIAL REMANESCENTE]" in rendered
    assert "status=UNIFORM_ALLOWANCE_COMPLIANT" in rendered
    assert "max_residual_stock_mm=0.000000000" in rendered
    assert "AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE" in rendered
    assert "[FLEXÃO ELÁSTICA DA PEÇA]" in rendered
    assert "radial_cutting_force_N=" in rendered
    assert "calculated_stiffness_n_per_mm=" in rendered
    assert "max_deflection_um=" in rendered
    assert "deflection_status=ELASTIC_DEFLECTION_COMPLIANT" in rendered
    assert (
        "ESTIMATIVA ANALÍTICA DE FLEXÃO ELÁSTICA DA PEÇA - NÃO CONSIDERA "
        "CONTAPONTO OU LUNETA DE APOIO" in rendered
    )
