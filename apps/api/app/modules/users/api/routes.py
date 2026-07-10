from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/users", tags=["users"])


class UserPreview(BaseModel):
    id: str
    name: str
    email: str
    role: str


@router.get("", response_model=list[UserPreview])
def list_users() -> list[UserPreview]:
    return []
