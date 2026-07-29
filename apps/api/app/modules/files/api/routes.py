from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import AuthorizationDependency
from app.modules.files.models import FileAsset
from app.modules.files.schemas import FileCreate, FileRead
from app.modules.projects.models import Project

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileRead])
def list_files(
    authorization: AuthorizationDependency,
    project_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[FileAsset]:
    stmt = select(FileAsset).join(Project).order_by(FileAsset.created_at)
    if project_id is not None:
        authorization.require_project_access(project_id)
        stmt = stmt.where(FileAsset.project_id == project_id)
    elif not authorization.is_admin:
        stmt = stmt.where(Project.owner_id == authorization.current_user.id)
    return list(db.scalars(stmt))


@router.post("", response_model=FileRead, status_code=201)
def create_file(
    payload: FileCreate,
    authorization: AuthorizationDependency,
    db: Session = Depends(get_db),
) -> FileAsset:
    authorization.require_project_access(payload.project_id)

    file_asset = FileAsset(
        project_id=payload.project_id,
        filename=payload.filename,
        type=payload.type,
        storage_key=payload.storage_key,
    )
    db.add(file_asset)
    db.commit()
    db.refresh(file_asset)
    return file_asset
