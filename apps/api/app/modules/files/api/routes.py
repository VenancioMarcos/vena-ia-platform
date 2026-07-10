from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/files", tags=["files"])


class FilePreview(BaseModel):
    id: str
    project_id: str
    filename: str
    type: str


@router.get("", response_model=list[FilePreview])
def list_files() -> list[FilePreview]:
    return []

