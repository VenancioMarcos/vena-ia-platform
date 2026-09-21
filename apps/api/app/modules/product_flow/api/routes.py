from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.product_flow.models import ControlledResultRecord, ResultFeedback
from app.modules.product_flow.schemas import (
    FeedbackCreate,
    FeedbackRead,
    HumanReviewRead,
    HumanReviewRequest,
)
from app.modules.product_flow.service import ProductFlowService

router = APIRouter(prefix="/product-flow", tags=["product-flow"])


def _service(db: Session, current_user: CurrentUserDependency) -> ProductFlowService:
    return ProductFlowService(db, current_user)


@router.get("/results/{result_id}/review", response_model=HumanReviewRead)
def get_human_review(
    result_id: str,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> ControlledResultRecord:
    return _service(db, current_user).get_result(result_id)


@router.post("/results/{result_id}/review", response_model=HumanReviewRead)
def approve_human_review(
    result_id: str,
    payload: HumanReviewRequest,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> ControlledResultRecord:
    return _service(db, current_user).approve_review(result_id, payload)


@router.get("/results/{result_id}/feedback", response_model=FeedbackRead)
def get_feedback(
    result_id: str,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> ResultFeedback:
    return _service(db, current_user).get_feedback(result_id)


@router.post("/results/{result_id}/feedback", response_model=FeedbackRead, status_code=201)
def create_feedback(
    result_id: str,
    payload: FeedbackCreate,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> ResultFeedback:
    return _service(db, current_user).create_feedback(result_id, payload)
