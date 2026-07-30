from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.manufacturing.schemas import MillingInput, MillingRecommendation
from app.modules.manufacturing.service import MillingRecommendationService

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])


@router.post("/milling/recommendation", response_model=MillingRecommendation)
def recommend_milling(
    payload: MillingInput,
    _current_user: CurrentUserDependency,
) -> MillingRecommendation:
    return MillingRecommendationService().recommend(payload)
