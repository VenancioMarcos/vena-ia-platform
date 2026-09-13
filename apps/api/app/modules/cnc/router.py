from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cam.repository import TurningPlanNotFoundError, TurningPlanStoreDependency
from app.modules.cam.schemas import TurningStrategyPlanResponse
from app.modules.cnc.enums import FeedMode, SpindleMode
from app.modules.cnc.schemas import (
    GCodeGatewayRequest,
    GCodeGenerationRequest,
    GCodeGenerationResponse,
    ToolpathSimulationPayload,
    ToolpathSimulationRequest,
)
from app.modules.cnc.services.envelope_validator import KinematicBoundaryViolation
from app.modules.cnc.services.gcode_formatter import GCodeFormattingError, format_gcode_candidate
from app.modules.cnc.services.simulation_parser import (
    ToolpathSimulationError,
    parse_toolpath_simulation,
)


router = APIRouter(prefix="/api/v1/cnc", tags=["cnc-generation"])


@router.post("/turning/generate", response_model=GCodeGenerationResponse)
def generate_turning_gcode_candidate(
    payload: GCodeGatewayRequest,
    current_user: CurrentUserDependency,
    plan_store: TurningPlanStoreDependency,
) -> GCodeGenerationResponse:
    try:
        record = plan_store.get_owned(payload.plan_id, owner_user_id=str(current_user.id))
    except TurningPlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="CAM turning plan not found") from exc

    try:
        cam_plan = TurningStrategyPlanResponse(
            operation_type=record.response.operation_type,
            passes=record.response.passes,
            material_removal_volume_mm3=record.response.material_removal_volume_mm3,
            warnings=record.response.warnings,
        )
        request = GCodeGenerationRequest(
            plan_id=record.response.plan_id,
            cam_plan_data=cam_plan,
            controller_profile=payload.controller_profile,
            program_number=payload.program_number,
            machine_envelope=payload.machine_envelope,
            review_authentication="AUTHENTICATED_REVIEW_CONTEXT",
            feed_mode=FeedMode.G95_PER_REVOLUTION,
            spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
            feed_value=record.request.cutting_params.feed_mm_per_rev,
            spindle_value=record.request.cutting_params.vc_m_per_min,
            max_spindle_rpm=payload.max_spindle_rpm,
            max_feed_mm_min=payload.max_feed_mm_min,
            tool_number=payload.tool_number,
            tool_offset=payload.tool_offset,
            tool_name=payload.tool_name,
        )
        return format_gcode_candidate(request)
    except (GCodeFormattingError, KinematicBoundaryViolation, ValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/turning/simulate-toolpath",
    response_model=ToolpathSimulationPayload,
)
def simulate_turning_toolpath(
    payload: ToolpathSimulationRequest,
    current_user: CurrentUserDependency,
    plan_store: TurningPlanStoreDependency,
) -> ToolpathSimulationPayload:
    program_text = payload.program_text
    if payload.plan_id is not None:
        try:
            record = plan_store.get_owned(
                payload.plan_id,
                owner_user_id=str(current_user.id),
            )
        except TurningPlanNotFoundError as exc:
            raise HTTPException(status_code=404, detail="CAM turning plan not found") from exc

        try:
            cam_plan = TurningStrategyPlanResponse(
                operation_type=record.response.operation_type,
                passes=record.response.passes,
                material_removal_volume_mm3=record.response.material_removal_volume_mm3,
                warnings=record.response.warnings,
            )
            generated = format_gcode_candidate(
                GCodeGenerationRequest(
                    plan_id=record.response.plan_id,
                    cam_plan_data=cam_plan,
                    controller_profile=payload.controller_profile,
                    program_number=payload.program_number,
                    machine_envelope=payload.machine_envelope,
                    review_authentication="AUTHENTICATED_REVIEW_CONTEXT",
                    feed_mode=FeedMode.G95_PER_REVOLUTION,
                    spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
                    feed_value=record.request.cutting_params.feed_mm_per_rev,
                    spindle_value=record.request.cutting_params.vc_m_per_min,
                    max_spindle_rpm=payload.max_spindle_rpm,
                    max_feed_mm_min=payload.max_feed_mm_min,
                    tool_number=payload.tool_number,
                    tool_offset=payload.tool_offset,
                    tool_name=payload.tool_name,
                )
            )
            program_text = generated.program_text
        except (GCodeFormattingError, KinematicBoundaryViolation, ValidationError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    if program_text is None:  # guarded by ToolpathSimulationRequest
        raise HTTPException(status_code=422, detail="SIMULATION_SOURCE_REQUIRED")
    try:
        return parse_toolpath_simulation(
            program_text,
            controller_profile=payload.controller_profile,
            machine_envelope=payload.machine_envelope,
            stock=payload.stock,
            source_plan_id=payload.plan_id,
        )
    except (KinematicBoundaryViolation, ToolpathSimulationError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
