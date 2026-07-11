from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.models import Project
from app.modules.projects.schemas import ProjectCreate, ProjectRead
from app.modules.users.models import User

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(
    owner_id: str | None = None, db: Session = Depends(get_db)
) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at)
    if owner_id:
        stmt = stmt.where(Project.owner_id == owner_id)
    return list(db.scalars(stmt))


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    owner = db.get(User, payload.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner (user) not found")

    project = Project(name=payload.name, owner_id=payload.owner_id, status=payload.status)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
