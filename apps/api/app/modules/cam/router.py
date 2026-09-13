from uuid import NAMESPACE_URL, uuid5

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cad.dependencies import CadIngestionGatewayDependency
from app.modules.cad.ingestion import CadIngestionJobNotFoundError
from app.modules.cam.schemas import (
    RzPoint,
    TurningBoundingBox,
    TurningPlanGatewayRequest,
    TurningPlanGatewayResponse,
    TurningStrategyPlanRequest,
)
from app.modules.cam.services.strategy_engine import (
    TurningStrategyValidationError,
    plan_turning_strategy,
)


router = APIRouter(prefix="/api/v1/cam", tags=["cam-planning"])


@router.post("/turning/plan", response_model=TurningPlanGatewayResponse)
def create_turning_plan(
    payload: TurningPlanGatewayRequest,
    current_user: CurrentUserDependency,
    gateway: CadIngestionGatewayDependency,
) -> TurningPlanGatewayResponse:
    try:
        job = gateway.get_job(payload.cad_job_id, owner_user_id=str(current_user.id))
    except CadIngestionJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail="CAD ingestion job not found") from exc

    profile = job.profile_data
    if (
        job.status != "COMPLETED"
        or profile is None
        or profile.review_status != "PROFILE_AVAILABLE_REQUIRES_REVIEW"
    ):
        raise HTTPException(status_code=422, detail="CAD_JOB_PROFILE_NOT_REVIEWABLE")

    try:
        request = TurningStrategyPlanRequest(
            operation_type=payload.operation_type,
            profile_data=tuple(
                RzPoint(r_mm=point.r_mm, z_mm=point.z_mm) for point in profile.points
            ),
            bounding_box=TurningBoundingBox(
                max_radius_mm=profile.bounding_box.max_radius_mm,
                min_z_mm=profile.bounding_box.min_z_mm,
                max_z_mm=profile.bounding_box.max_z_mm,
                total_z_length_mm=profile.bounding_box.total_z_length_mm,
            ),
            linear_tolerance_mm=payload.linear_tolerance_mm,
            material_reference=payload.material_reference,
            stock_radius_mm=payload.stock_radius_mm,
            stock_front_z_mm=payload.stock_front_z_mm,
            target_front_z_mm=payload.target_front_z_mm,
            finish_allowance_mm=payload.finish_allowance_mm,
            tool=payload.tool_params,
            cutting_parameters=payload.cutting_params,
            review_status=profile.review_status,
        )
        plan = plan_turning_strategy(request)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="CAM_PLAN_INPUT_INVALID") from exc
    except TurningStrategyValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    plan_id = str(
        uuid5(
            NAMESPACE_URL,
            ":".join(
                (
                    "vena-ia-cam-plan-v1",
                    str(current_user.id),
                    job.job_id,
                    profile.model_dump_json(),
                    payload.model_dump_json(),
                )
            ),
        )
    )
    warnings = tuple(dict.fromkeys((*profile.warnings, *plan.warnings)))
    return TurningPlanGatewayResponse(
        plan_id=plan_id,
        cad_job_id=job.job_id,
        operation_type=plan.operation_type,
        passes=plan.passes,
        material_removal_volume_mm3=plan.material_removal_volume_mm3,
        warnings=warnings,
    )
