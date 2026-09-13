from dataclasses import replace
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.cam.repository import TurningPlanRecord
from app.modules.cam.schemas import TurningPlanGatewayRequest, TurningPlanGatewayResponse
from app.modules.cnc.enums import CNCControllerType, SpindleMode
from app.modules.cnc.schemas import (
    GCodeSafetyFlags,
    MachiningTechnicalReportPayload,
    ToolpathSimulationRequest,
)
from app.modules.cnc.services.gcode_formatter import format_gcode_candidate
from app.modules.cnc.services.machining_report import (
    MachiningReportSource,
    compile_machining_report,
    plan_fingerprint,
)
from tests.unit.cnc.test_gcode_formatter import _request
from tests.unit.cnc.test_simulation_parser import _stock


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
        material_reference="synthetic",
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
