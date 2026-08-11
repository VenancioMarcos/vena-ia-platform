from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
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
from app.modules.engineering.manufacturing import (
    ManufacturingPlanningError,
    ManufacturingPlanningService,
)
from app.modules.engineering.manufacturing_schemas import (
    ManufacturingGeometryModel,
    ManufacturingPlanningRequest,
)
from app.modules.engineering.toolpath import ToolpathCandidateError, ToolpathCandidateService
from app.modules.engineering.toolpath_schemas import ToolpathCandidate, ToolpathCandidateRequest
from app.modules.engineering.postprocessor import PostprocessorError, SyntheticPostprocessor
from app.modules.engineering.postprocessor_schemas import GCodeCandidate, GCodeCandidateRequest
from app.modules.engineering.level2 import Level2Verifier
from app.modules.engineering.level2_schemas import (
    Level2VerificationEvidence,
    Level2VerificationRequest,
)
from app.modules.engineering.blind_validation import ControlledBlindValidationService
from app.modules.engineering.blind_validation_schemas import (
    ControlledBlindValidationEvidence,
    ControlledBlindValidationRequest,
)
from app.modules.engineering.g9_review import G9ReviewPackageError
from app.modules.engineering.digital_thread import (
    BoundedManufacturingIntelligenceService,
    DigitalThreadError,
    DigitalThreadService,
)
from app.modules.engineering.digital_thread_schemas import (
    BoundedIntelligenceRequest,
    BoundedIntelligenceResponse,
    DigitalThreadBuildRequest,
    DigitalThreadManifest,
)
from app.modules.engineering.controlled_environment import (
    ControlledEnvironmentError,
    ControlledEnvironmentService,
)
from app.modules.engineering.controlled_environment_schemas import (
    ControlledDownloadRequest,
    ControlledEnvironmentRequest,
    ControlledEnvironmentResult,
)
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.schemas import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogGovernanceEvidence,
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
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.service import OrganizationAuthorization

router = APIRouter(prefix="/engineering", tags=["engineering"])


def _catalog_service(db: Session, current_user: CurrentUserDependency) -> EngineeringCatalogService:
    return EngineeringCatalogService(
        EngineeringCatalogRepository(db),
        OrganizationAuthorization(OrganizationRepository(db), current_user),
    )


@router.post("/catalogs", response_model=CatalogItemRead, status_code=201)
def create_catalog_item(
    payload: CatalogItemCreate,
    current_user: CurrentUserDependency,
    organization_id: Annotated[str, Query(min_length=1, max_length=36)],
    db: Session = Depends(get_db),
) -> EngineeringCatalogItem:
    return _catalog_service(db, current_user).create(payload, current_user.id, organization_id)


@router.get("/catalogs", response_model=list[CatalogItemRead])
def list_catalog_items(
    current_user: CurrentUserDependency,
    organization_id: Annotated[str | None, Query(min_length=1, max_length=36)] = None,
    kind: CatalogKind | None = None,
    db: Session = Depends(get_db),
) -> list[EngineeringCatalogItem]:
    return _catalog_service(db, current_user).list(organization_id=organization_id, kind=kind)


@router.get(
    "/catalogs/{catalog_id}/governance",
    response_model=CatalogGovernanceEvidence,
)
def get_catalog_governance(
    catalog_id: str,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> CatalogGovernanceEvidence:
    return _catalog_service(db, current_user).governance(catalog_id)


@router.post("/selections/preliminary", response_model=PreliminarySelection)
def select_preliminary(
    payload: SelectionRequest, current_user: CurrentUserDependency, db: Session = Depends(get_db)
) -> PreliminarySelection:
    return _catalog_service(db, current_user).select(payload)


@router.post("/recommendations/preliminary", response_model=EngineeringRecommendation)
def recommend_preliminary(
    payload: RecommendationRequest,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> EngineeringRecommendation:
    return _catalog_service(db, current_user).recommend(payload)


@router.post("/reports/preliminary", response_model=EngineeringReviewReport)
def report_preliminary(
    payload: RecommendationRequest,
    current_user: CurrentUserDependency,
    db: Session = Depends(get_db),
) -> EngineeringReviewReport:
    return _catalog_service(db, current_user).report(payload)


@router.post("/planning/from-document-feature", response_model=FeaturePlanningResponse)
def plan_from_document_feature(
    payload: FeaturePlanningRequest,
    current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> FeaturePlanningResponse:
    try:
        return FeaturePlanningBridge(
            cad,
            _catalog_service(db, current_user),
        ).plan(payload)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StepParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/planning/manufacturing-geometry",
    response_model=ManufacturingGeometryModel,
)
def plan_manufacturing_geometry(
    payload: ManufacturingPlanningRequest,
    current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> ManufacturingGeometryModel:
    try:
        return ManufacturingPlanningService(cad, _catalog_service(db, current_user)).plan(payload)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (StepParseError, ManufacturingPlanningError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/planning/toolpath-candidate", response_model=ToolpathCandidate)
def create_toolpath_candidate(
    payload: ToolpathCandidateRequest,
    _current_user: CurrentUserDependency,
) -> ToolpathCandidate:
    try:
        return ToolpathCandidateService().create(payload)
    except ToolpathCandidateError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/planning/gcode-candidate", response_model=GCodeCandidate)
def create_gcode_candidate(
    payload: GCodeCandidateRequest,
    _current_user: CurrentUserDependency,
) -> GCodeCandidate:
    try:
        return SyntheticPostprocessor().generate(payload)
    except PostprocessorError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/planning/level2-verification", response_model=Level2VerificationEvidence)
def verify_level2(
    payload: Level2VerificationRequest,
    _current_user: CurrentUserDependency,
) -> Level2VerificationEvidence:
    return Level2Verifier().verify(payload)


@router.post(
    "/planning/controlled-blind-validation",
    response_model=ControlledBlindValidationEvidence,
)
def freeze_controlled_blind_validation(
    payload: ControlledBlindValidationRequest,
    _current_user: CurrentUserDependency,
) -> ControlledBlindValidationEvidence:
    return ControlledBlindValidationService().freeze(payload)


@router.post("/digital-thread", response_model=DigitalThreadManifest)
def build_digital_thread(
    payload: DigitalThreadBuildRequest,
    current_user: CurrentUserDependency,
    organization_id: Annotated[str, Query(min_length=1, max_length=36)],
    db: Session = Depends(get_db),
) -> DigitalThreadManifest:
    OrganizationAuthorization(OrganizationRepository(db), current_user).require_organization(
        organization_id
    )
    try:
        return DigitalThreadService().build(payload, organization_id)
    except DigitalThreadError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/digital-thread/intelligence", response_model=BoundedIntelligenceResponse)
def analyze_digital_thread(
    payload: BoundedIntelligenceRequest,
    current_user: CurrentUserDependency,
    organization_id: Annotated[str, Query(min_length=1, max_length=36)],
    db: Session = Depends(get_db),
) -> BoundedIntelligenceResponse:
    OrganizationAuthorization(OrganizationRepository(db), current_user).require_organization(
        organization_id
    )
    if payload.thread.organization_id != organization_id or (
        payload.baseline is not None and payload.baseline.organization_id != organization_id
    ):
        raise HTTPException(status_code=404, detail="Digital thread not found")
    return BoundedManufacturingIntelligenceService().analyze(payload)


@router.post(
    "/controlled-environment/runs",
    response_model=ControlledEnvironmentResult,
)
def run_controlled_environment(
    payload: ControlledEnvironmentRequest,
    current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> ControlledEnvironmentResult:
    OrganizationAuthorization(OrganizationRepository(db), current_user).require_organization(
        payload.organization_id
    )
    try:
        return ControlledEnvironmentService(
            cad,
            _catalog_service(db, current_user),
            settings.auth_secret_key,
        ).run(payload, current_user.id)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (
        StepParseError,
        ManufacturingPlanningError,
        ToolpathCandidateError,
        PostprocessorError,
        ControlledEnvironmentError,
        G9ReviewPackageError,
    ) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail="Generated controlled evidence failed validation.",
        ) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/controlled-environment/download", response_class=Response)
def download_controlled_candidate(
    payload: ControlledDownloadRequest,
    current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> Response:
    OrganizationAuthorization(OrganizationRepository(db), current_user).require_organization(
        payload.organization_id
    )
    try:
        program = ControlledEnvironmentService(
            cad,
            _catalog_service(db, current_user),
            settings.auth_secret_key,
        ).validate_download(payload, current_user.id)
    except ControlledEnvironmentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    filename = f"vena-ia-{payload.gcode_candidate.output_hash[:16]}.candidate.nc"
    return Response(
        content=program,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Vena-IA-Classification": "CANDIDATE_FOR_VALIDATION",
            "X-Vena-IA-Physical-Use-Authorized": "false",
            "X-Vena-IA-Review-State": "REQUIRES_HUMAN_REVIEW",
        },
    )
