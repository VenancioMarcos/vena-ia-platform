from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatStatus(BaseModel):
    status: str
    assistant: str
    capabilities: list[str]


@router.get("", response_model=ChatStatus)
def chat_status() -> ChatStatus:
    return ChatStatus(
        status="ready",
        assistant="Vena_IA",
        capabilities=["engineering-assistance", "project-context", "rag-planned"],
    )

