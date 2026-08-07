from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.ai.dependencies import AIServiceDependency
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cad.dependencies import CADAnalysisServiceDependency
from app.modules.cad.parser import StepParseError
from app.modules.cad.service import CADContentUnavailableError
from app.modules.cnc.service import CNCPlanningService
from app.modules.documents.dependencies import KnowledgeServiceDependency
from app.modules.documents.service import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    InvalidDocumentError,
    ProjectNotFoundError,
)
from app.modules.engineering.assistance import SpecializedAssistanceService
from app.modules.engineering.assistance_schemas import (
    SpecializedAssistanceRequest,
    SpecializedAssistanceResponse,
)
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.service import EngineeringCatalogService
from app.modules.engineering.workflow import IntegratedEngineeringWorkflowService
from app.modules.research.dependencies import ResearchServiceDependency
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.service import OrganizationAuthorization

router = APIRouter(prefix="/engineering", tags=["engineering-assistance"])


@router.post("/workflow-assistance", response_model=SpecializedAssistanceResponse)
def create_workflow_assistance(
    payload: SpecializedAssistanceRequest,
    current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    knowledge: KnowledgeServiceDependency,
    research: ResearchServiceDependency,
    ai: AIServiceDependency,
    db: Session = Depends(get_db),
) -> SpecializedAssistanceResponse:
    try:
        workflow = IntegratedEngineeringWorkflowService(
            cad,
            EngineeringCatalogService(
                EngineeringCatalogRepository(db),
                OrganizationAuthorization(OrganizationRepository(db), current_user),
            ),
            CNCPlanningService(),
        )
        return SpecializedAssistanceService(
            workflow,
            knowledge,
            research,
            ai,
            provider=settings.rag_ai_provider,
            chat_model=settings.rag_chat_model,
        ).assist(payload)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StepParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
