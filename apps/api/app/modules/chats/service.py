from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.authorization import AuthorizationService
from app.modules.chats.models import Chat, Message
from app.modules.documents.knowledge import KnowledgeService
from app.modules.projects.models import Project


class ChatGenerationError(Exception):
    pass


class ChatService:
    def __init__(
        self,
        db: Session,
        authorization: AuthorizationService,
        knowledge: KnowledgeService,
    ) -> None:
        self._db = db
        self._authorization = authorization
        self._knowledge = knowledge

    def list_messages(self, project_id: str) -> list[Message]:
        self._authorization.require_project_access(project_id)
        chat = self._db.scalar(select(Chat).where(Chat.project_id == project_id))
        return list(chat.messages) if chat else []

    def create_user_message(self, project_id: str, content: str) -> Message:
        project = self._authorization.require_project_access(project_id)
        chat = self._get_or_create_chat(project)
        message = Message(
            chat_id=chat.id,
            user_id=self._authorization.current_user.id,
            role="user",
            content=content,
            status="COMPLETED",
            evidence=[],
        )
        self._db.add(message)
        self._db.commit()
        self._db.refresh(message)
        return message

    def ask(
        self,
        project_id: str,
        question: str,
        limit: int,
    ) -> tuple[Message, Message]:
        project = self._authorization.require_project_access(project_id)
        chat = self._get_or_create_chat(project)
        user_message = Message(
            chat_id=chat.id,
            user_id=self._authorization.current_user.id,
            role="user",
            content=question,
            status="PENDING",
            evidence=[],
        )
        self._db.add(user_message)
        self._db.commit()
        self._db.refresh(user_message)
        try:
            answer = self._knowledge.answer(project_id, question, limit)
        except Exception as exc:
            user_message.status = "FAILED"
            user_message.error = "Serviço de IA indisponível; tente novamente."
            self._db.commit()
            raise ChatGenerationError("Unable to generate grounded response") from exc

        evidence = [
            {
                "document_id": match.chunk.document_id,
                "page_number": match.chunk.page_number,
                "chunk_index": match.chunk.chunk_index,
                "score": match.score,
                "excerpt": match.chunk.content[:1_000],
            }
            for match in answer.matches
        ]
        assistant_message = Message(
            chat_id=chat.id,
            user_id=self._authorization.current_user.id,
            role="assistant",
            content=answer.answer,
            status="COMPLETED",
            evidence=evidence,
        )
        user_message.status = "COMPLETED"
        self._db.add(assistant_message)
        self._db.commit()
        self._db.refresh(user_message)
        self._db.refresh(assistant_message)
        return user_message, assistant_message

    def _get_or_create_chat(self, project: Project) -> Chat:
        chat = self._db.scalar(select(Chat).where(Chat.project_id == project.id))
        if chat is None:
            chat = Chat(project_id=project.id, title=f"Chat - {project.name}")
            self._db.add(chat)
            self._db.commit()
            self._db.refresh(chat)
        return chat
