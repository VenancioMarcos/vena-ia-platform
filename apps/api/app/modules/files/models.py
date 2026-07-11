import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FileAsset(Base):
    """Metadata for a technical file (PDF, STEP, STL, DXF, IGES) attached to a project.

    Storage of the file's binary content in MinIO is planned for v0.4
    (docs/ROADMAP.md). This table currently tracks metadata only.
    """

    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    project: Mapped["Project"] = relationship(back_populates="files")  # noqa: F821
