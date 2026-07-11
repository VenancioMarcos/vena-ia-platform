from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.files.models import FileAsset
from app.modules.files.schemas import FileCreate, FileRead
from app.modules.projects.models import Project

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileRead])
def list_files(project_id: str | None = None, db: Session = Depends(get_db)) -> list[FileAsset]:
    stmt = select(FileAsset).order_by(FileAsset.created_at)
    if project_id:
        stmt = stmt.where(FileAsset.project_id == project_id)
    return list(db.scalars(stmt))


@router.post("", response_model=FileRead, status_code=201)
def create_file(payload: FileCreate, db: Session = Depends(get_db)) -> FileAsset:
    project = db.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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
