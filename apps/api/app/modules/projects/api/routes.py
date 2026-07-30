from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.models import Project
from app.modules.projects.schemas import ProjectCreate, ProjectRead
from app.modules.auth.dependencies import AuthorizationDependency

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(
    authorization: AuthorizationDependency,
    owner_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at)
    authorized_owner = authorization.authorized_owner_filter(owner_id)
    if authorized_owner:
        stmt = stmt.where(Project.owner_id == authorized_owner)
    return list(db.scalars(stmt))


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    payload: ProjectCreate,
    authorization: AuthorizationDependency,
    db: Session = Depends(get_db),
) -> Project:
    project = Project(
        name=payload.name,
        owner_id=authorization.current_user.id,
        status=payload.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: str,
    authorization: AuthorizationDependency,
) -> Project:
    return authorization.require_project_access(project_id)
