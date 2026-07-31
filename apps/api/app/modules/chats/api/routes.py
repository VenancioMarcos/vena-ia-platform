from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.auth.dependencies import AuthorizationDependency
from app.modules.chats.dependencies import ChatServiceDependency
from app.modules.chats.schemas import (
    ChatAskRequest,
    ChatAskResponse,
    MessageCreate,
    MessageRead,
)
from app.modules.chats.service import ChatGenerationError

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatStatus(BaseModel):
    status: str
    assistant: str
    capabilities: list[str]


@router.get("", response_model=ChatStatus)
def chat_status(_authorization: AuthorizationDependency) -> ChatStatus:
    return ChatStatus(
        status="ready",
        assistant="Vena_IA",
        capabilities=[
            "grounded-project-knowledge",
            "persistent-history",
            "traceable-evidence",
        ],
    )


@router.get("/{project_id}/messages", response_model=list[MessageRead])
def list_messages(
    project_id: str,
    service: ChatServiceDependency,
) -> list[MessageRead]:
    return [
        MessageRead.model_validate(message)
        for message in service.list_messages(project_id)
    ]


@router.post("/{project_id}/messages", response_model=MessageRead, status_code=201)
def create_message(
    project_id: str,
    payload: MessageCreate,
    service: ChatServiceDependency,
) -> MessageRead:
    if payload.role != "user":
        raise HTTPException(status_code=422, detail="Only user messages may be submitted")
    return MessageRead.model_validate(
        service.create_user_message(project_id, payload.content)
    )


@router.post("/{project_id}/ask", response_model=ChatAskResponse)
def ask_project_chat(
    project_id: str,
    payload: ChatAskRequest,
    service: ChatServiceDependency,
) -> ChatAskResponse:
    try:
        user_message, assistant_message = service.ask(
            project_id, payload.question, payload.limit
        )
    except ChatGenerationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate grounded response",
        ) from exc
    return ChatAskResponse(
        user_message=MessageRead.model_validate(user_message),
        assistant_message=MessageRead.model_validate(assistant_message),
    )
