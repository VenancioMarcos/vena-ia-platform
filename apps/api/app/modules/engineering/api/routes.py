from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cad.dependencies import CADAnalysisServiceDependency
from app.modules.cad.parser import StepParseError
from app.modules.cad.service import CADContentUnavailableError
from app.modules.documents.service import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    InvalidDocumentError,
    ProjectNotFoundError,
)
from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.schemas import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogKind,
    EngineeringRecommendation,
    EngineeringReviewReport,
    FeaturePlanningRequest,
    FeaturePlanningResponse,
    PreliminarySelection,
    RecommendationRequest,
    SelectionRequest,
)
from app.modules.engineering.service import EngineeringCatalogService
from app.modules.engineering.planning import FeaturePlanningBridge

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


@router.post("/planning/from-document-feature", response_model=FeaturePlanningResponse)
def plan_from_document_feature(
    payload: FeaturePlanningRequest,
    _current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> FeaturePlanningResponse:
    try:
        return FeaturePlanningBridge(
            cad,
            EngineeringCatalogService(EngineeringCatalogRepository(db)),
        ).plan(payload)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StepParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
