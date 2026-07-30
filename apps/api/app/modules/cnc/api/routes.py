from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cnc.schemas import CNCPlanPreview, CNCPlanRequest
from app.modules.cnc.service import CNCPlanningService

router = APIRouter(prefix="/cnc", tags=["cnc"])


@router.post("/plan/preview", response_model=CNCPlanPreview)
def preview_cnc_plan(
    payload: CNCPlanRequest,
    _current_user: CurrentUserDependency,
) -> CNCPlanPreview:
    return CNCPlanningService().preview(payload)
