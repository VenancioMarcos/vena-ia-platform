from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectPreview(BaseModel):
    id: str
    name: str
    status: str


@router.get("", response_model=list[ProjectPreview])
def list_projects() -> list[ProjectPreview]:
    return []

