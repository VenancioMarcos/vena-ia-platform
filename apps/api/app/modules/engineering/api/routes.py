from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.schemas import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogKind,
    EngineeringRecommendation,
    EngineeringReviewReport,
    PreliminarySelection,
    RecommendationRequest,
    SelectionRequest,
)
from app.modules.engineering.service import EngineeringCatalogService

router = APIRouter(prefix="/engineering", tags=["engineering"])


@router.post("/catalogs", response_model=CatalogItemRead, status_code=201)
def create_catalog_item(
    payload: CatalogItemCreate, current_user: CurrentUserDependency, db: Session = Depends(get_db)
) -> EngineeringCatalogItem:
    return EngineeringCatalogService(EngineeringCatalogRepository(db)).create(
        payload, current_user.id
    )


@router.get("/catalogs", response_model=list[CatalogItemRead])
def list_catalog_items(
    _current_user: CurrentUserDependency,
    kind: CatalogKind | None = None,
    db: Session = Depends(get_db),
) -> list[EngineeringCatalogItem]:
    return EngineeringCatalogRepository(db).list(kind.value if kind else None)


@router.post("/selections/preliminary", response_model=PreliminarySelection)
def select_preliminary(
    payload: SelectionRequest, _current_user: CurrentUserDependency, db: Session = Depends(get_db)
) -> PreliminarySelection:
    return EngineeringCatalogService(EngineeringCatalogRepository(db)).select(payload)


@router.post("/recommendations/preliminary", response_model=EngineeringRecommendation)
def recommend_preliminary(
    payload: RecommendationRequest,
    _current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> EngineeringRecommendation:
    return EngineeringCatalogService(EngineeringCatalogRepository(db)).recommend(payload)


@router.post("/reports/preliminary", response_model=EngineeringReviewReport)
def report_preliminary(
    payload: RecommendationRequest,
    _current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> EngineeringReviewReport:
    return EngineeringCatalogService(EngineeringCatalogRepository(db)).report(payload)
