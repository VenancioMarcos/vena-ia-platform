from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import AuthorizationDependency
from app.modules.chats.service import ChatService
from app.modules.documents.dependencies import KnowledgeServiceDependency


def get_chat_service(
    db: Annotated[Session, Depends(get_db)],
    authorization: AuthorizationDependency,
    knowledge: KnowledgeServiceDependency,
) -> ChatService:
    return ChatService(db, authorization, knowledge)


ChatServiceDependency = Annotated[ChatService, Depends(get_chat_service)]
