"""Compile review-only reports from server-generated, plan-bound simulation sources."""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import math

from app.modules.cam.repository import TurningPlanRecord
from app.modules.cam.schemas import (
    TurningPlanGatewayRequest,
    TurningPlanGatewayResponse,
    TurningStrategyPlanResponse,
)
from app.modules.cnc.enums import FeedMode, SpindleMode
from app.modules.cnc.schemas import (
    GCodeGenerationRequest,
    MachiningReportTool,
    MachiningTechnicalReportPayload,
    ToolpathSimulationRequest,
)
from app.modules.cnc.services.gcode_formatter import format_gcode_candidate
from app.modules.cnc.services.cost_time_estimator import estimate_machining_cost_time
from app.modules.cnc.services.geometry_auditor import (
    GeometryDimensionalAuditError,
    require_geometry_dimensions_consistent,
)
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.roughness_estimator import estimate_surface_roughness
from app.modules.cnc.services.simulation_parser import parse_toolpath_simulation
from app.modules.cnc.services.sustainability_estimator import estimate_sustainability
from app.modules.cnc.services.syntax_linter import require_valid_gcode_syntax
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


class MachiningReportError(ValueError):
    pass


def plan_fingerprint(record: TurningPlanRecord) -> str:
    request = TurningPlanGatewayRequest.model_validate(record.request)
    response = TurningPlanGatewayResponse.model_validate(record.response)
    if (
        request.cad_job_id != response.cad_job_id
        or request.operation_type != response.operation_type
    ):
        raise MachiningReportError("REPORT_PLAN_INCONSISTENT")
    if any(item.operation_type != response.operation_type for item in response.passes):
        raise MachiningReportError("REPORT_PLAN_INCONSISTENT")
    bounds = record.source_brep_bounds.model_dump_json()
    serialized = request.model_dump_json() + response.model_dump_json() + bounds
    return sha256(serialized.encode()).hexdigest()


@dataclass(frozen=True)
class MachiningReportSource:
    owner_user_id: str
    plan_fingerprint: str
    request: ToolpathSimulationRequest
    program_text: str
    captured_at: datetime


def compile_machining_report(
    record: TurningPlanRecord, source: MachiningReportSource
) -> MachiningTechnicalReportPayload:
    fingerprint = plan_fingerprint(record)
    request = ToolpathSimulationRequest.model_validate(source.request)
    if (
        source.owner_user_id != record.owner_user_id
        or request.plan_id != record.response.plan_id
        or source.plan_fingerprint != fingerprint
        or request.program_text is not None
    ):
        raise MachiningReportError("REPORT_SOURCE_MISMATCH")
    expected = format_gcode_candidate(
        GCodeGenerationRequest(
            plan_id=record.response.plan_id,
            cam_plan_data=TurningStrategyPlanResponse.model_validate(
                record.response.model_dump(exclude={"plan_id", "cad_job_id"})
            ),
            controller_profile=request.controller_profile,
            program_number=request.program_number,
            machine_envelope=request.machine_envelope,
            review_authentication="AUTHENTICATED_REVIEW_CONTEXT",
            feed_mode=FeedMode.G95_PER_REVOLUTION,
            spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
            feed_value=record.request.cutting_params.feed_mm_per_rev,
            spindle_value=record.request.cutting_params.vc_m_per_min,
            max_spindle_rpm=request.max_spindle_rpm,
            max_feed_mm_min=request.max_feed_mm_min,
            tool_number=request.tool_number,
            tool_offset=request.tool_offset,
            tool_name=request.tool_name,
        )
    )
    if expected.program_text != source.program_text:
        raise MachiningReportError("REPORT_PROGRAM_MISMATCH")
    require_valid_gcode_syntax(source.program_text, request.controller_profile)
    simulation = parse_toolpath_simulation(
        source.program_text,
        controller_profile=request.controller_profile,
        machine_envelope=request.machine_envelope,
        stock=request.stock,
        source_plan_id=request.plan_id,
    )
    estimate = simulation.cycle_time_estimate
    if estimate is None or not estimate.per_tool_breakdown:
        raise MachiningReportError("REPORT_TOOLPATH_REQUIRED")
    if any(item.active_tool is None for item in simulation.segments):
        raise MachiningReportError("REPORT_TOOL_REQUIRED")
    geometry_audit = require_geometry_dimensions_consistent(
        record.source_brep_bounds,
        simulation.segments,
        tolerance_mm=record.request.linear_tolerance_mm,
    )
    roughness_audit = estimate_surface_roughness(
        record.request.cutting_params.feed_mm_per_rev,
        record.request.tool_params.tip_radius_mm,
        nominal_ra_max_um=record.request.nominal_surface_roughness_ra_um,
    )
    reference_diameter_mm = record.source_brep_bounds.max_radius_mm * 2.0
    theoretical_rpm = (
        record.request.cutting_params.vc_m_per_min * 1_000.0
        / (math.pi * reference_diameter_mm)
    )
    power_force_audit = estimate_cutting_power_force(
        record.request.material_reference,
        feed_mm_per_rev=record.request.cutting_params.feed_mm_per_rev,
        depth_of_cut_mm=record.request.cutting_params.depth_of_cut_mm,
        cutting_edge_angle_deg=record.request.tool_params.cutting_edge_angle_deg,
        cutting_speed_m_per_min=record.request.cutting_params.vc_m_per_min,
        spindle_rpm_reference=min(theoretical_rpm, request.max_spindle_rpm),
        max_spindle_rpm=request.max_spindle_rpm,
        machine_power_limit_kw=record.request.machine_power_limit_kw,
    )
    tool_life_audits = tuple(
        estimate_tool_life(
            item.tool,
            record.request.material_reference,
            cutting_speed_m_per_min=record.request.cutting_params.vc_m_per_min,
            effective_cutting_time_minutes=item.cutting_time_seconds / 60.0,
        )
        for item in estimate.per_tool_breakdown
    )
    cost_time_audit = estimate_machining_cost_time(estimate, tool_life_audits)
    sustainability_audit = estimate_sustainability(
        motor_power_kw=power_force_audit.p_motor_est_kw,
        cutting_time_minutes=cost_time_audit.cutting_time_minutes,
        total_cycle_time_minutes=cost_time_audit.total_cycle_time_minutes,
    )
    return MachiningTechnicalReportPayload(
        plan_id=record.response.plan_id,
        cad_job_id=record.response.cad_job_id,
        controller_profile=request.controller_profile,
        program_number=request.program_number,
        program_sha256=sha256(source.program_text.encode()).hexdigest(),
        analytical_snapshot_at=source.captured_at,
        tools=tuple(
            MachiningReportTool(tool_id=item.tool, operations=(record.response.operation_type,))
            for item in estimate.per_tool_breakdown
        ),
        cycle_time_estimate=estimate,
        total_distance_mm=round(
            estimate.total_cutting_distance_mm + estimate.total_rapid_distance_mm, 9
        ),
        envelope_audit="PASS_DECLARED_2D_ENVELOPE_ONLY",
        machine_envelope=request.machine_envelope,
        chuck_proximity=simulation.chuck_proximity,
        geometry_audit=geometry_audit,
        surface_roughness_audit=roughness_audit,
        power_force_audit=power_force_audit,
        tool_life_audits=tool_life_audits,
        cost_time_audit=cost_time_audit,
        sustainability_audit=sustainability_audit,
        limitations=(
            "Source plan has no name; source_plan_name is unavailable.",
            "Timestamp identifies the analytical snapshot, not a machining event.",
            "Process-local latest successful simulation; rerun after restart or eviction.",
            "Route 6 estimate uses X-diameter/Z distances and its existing modal-feed model; "
            "G96/CSS RPM conversion is not physically validated.",
            "No acceleration, tool-change, dwell or physical cycle-time validation.",
            "Declared 2D envelope/proximity only; no G9 approval or machine authority.",
            "BRep nominal bounds passed the analytical dimensional gate.",
            "Surface roughness is an ideal kinematic estimate; vibration, tool wear and "
            "material effects are excluded.",
            "Kienzle force and power values are analytical estimates; real dynamic "
            "efficiency, thermal effects and machine behavior are excluded.",
            "Taylor tool-life values exclude real thermal fluctuations and lubrication.",
            "Cost and time values exclude logistics, unplanned downtime and taxes.",
            "Energy and carbon values exclude external cooling and startup power peaks.",
        ),
    )


__all__ = (
    "GeometryDimensionalAuditError",
    "MachiningReportError",
    "MachiningReportSource",
    "compile_machining_report",
    "plan_fingerprint",
)
