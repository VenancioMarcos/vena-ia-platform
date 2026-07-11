from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.chats.models import Chat, Message
from app.modules.chats.schemas import MessageCreate, MessageRead
from app.modules.projects.models import Project

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatStatus(BaseModel):
    status: str
    assistant: str
    capabilities: list[str]


@router.get("", response_model=ChatStatus)
def chat_status() -> ChatStatus:
    """Static capability descriptor for the chat module.

    Real AI-backed responses are planned for v0.3 - IA Base (docs/ROADMAP.md).
    In v0.2 this module only persists messages; it does not yet generate
    assistant replies.
    """
    return ChatStatus(
        status="ready",
        assistant="Vena_IA",
        capabilities=["engineering-assistance", "project-context", "rag-planned"],
    )


def _get_or_create_chat(project_id: str, db: Session) -> Chat:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    chat = db.scalar(select(Chat).where(Chat.project_id == project_id))
    if not chat:
        chat = Chat(project_id=project_id, title=f"Chat - {project.name}")
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat


@router.get("/{project_id}/messages", response_model=list[MessageRead])
def list_messages(project_id: str, db: Session = Depends(get_db)) -> list[Message]:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    chat = db.scalar(select(Chat).where(Chat.project_id == project_id))
    if not chat:
        return []
    return list(chat.messages)


@router.post("/{project_id}/messages", response_model=MessageRead, status_code=201)
def create_message(
    project_id: str, payload: MessageCreate, db: Session = Depends(get_db)
) -> Message:
    if payload.role not in {"user", "assistant"}:
        raise HTTPException(status_code=422, detail="role must be 'user' or 'assistant'")

    chat = _get_or_create_chat(project_id, db)
    message = Message(chat_id=chat.id, role=payload.role, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
