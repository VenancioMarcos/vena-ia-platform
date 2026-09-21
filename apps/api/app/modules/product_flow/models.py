import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ControlledResultRecord(Base):
    __tablename__ = "controlled_result_records"
    __table_args__ = (
        CheckConstraint(
            "review_state IN ('REQUIRES_HUMAN_REVIEW', "
            "'APPROVED_FOR_CONTROLLED_DOWNLOAD')",
            name="ck_controlled_result_review_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    result_version: Mapped[str] = mapped_column(String(64), nullable=False)
    gcode_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    digital_thread_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    blind_validation_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    download_token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    review_state: Mapped[str] = mapped_column(
        String(48), nullable=False, default="REQUIRES_HUMAN_REVIEW"
    )
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class ResultFeedback(Base):
    __tablename__ = "result_feedback"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_result_feedback_rating"),
        UniqueConstraint("result_id", "created_by", name="uq_result_feedback_result_user"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("controlled_result_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    result_version: Mapped[str] = mapped_column(String(64), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
