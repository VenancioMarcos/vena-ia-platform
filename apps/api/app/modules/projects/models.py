import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.chats.models import Chat
    from app.modules.documents.models import Document
    from app.modules.files.models import FileAsset
    from app.modules.users.models import User


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="projects")
    files: Mapped[list["FileAsset"]] = relationship(back_populates="project")
    documents: Mapped[list["Document"]] = relationship(back_populates="project")
    chats: Mapped[list["Chat"]] = relationship(back_populates="project")
