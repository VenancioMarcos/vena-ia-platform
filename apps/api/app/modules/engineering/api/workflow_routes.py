from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cad.dependencies import CADAnalysisServiceDependency
from app.modules.cad.parser import StepParseError
from app.modules.cad.service import CADContentUnavailableError
from app.modules.cnc.service import CNCPlanningService
from app.modules.documents.service import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    InvalidDocumentError,
    ProjectNotFoundError,
)
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.service import EngineeringCatalogService
from app.modules.engineering.workflow import IntegratedEngineeringWorkflowService
from app.modules.engineering.workflow_schemas import (
    IntegratedEngineeringWorkflow,
    IntegratedWorkflowRequest,
)

router = APIRouter(prefix="/engineering", tags=["engineering-workflow"])


@router.post("/workflows", response_model=IntegratedEngineeringWorkflow)
def create_integrated_workflow(
    payload: IntegratedWorkflowRequest,
    _current_user: CurrentUserDependency,
    cad: CADAnalysisServiceDependency,
    db: Session = Depends(get_db),
) -> IntegratedEngineeringWorkflow:
    try:
        return IntegratedEngineeringWorkflowService(
            cad,
            EngineeringCatalogService(EngineeringCatalogRepository(db)),
            CNCPlanningService(),
        ).execute(payload)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StepParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
