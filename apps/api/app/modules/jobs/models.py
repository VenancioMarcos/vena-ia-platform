import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.modules.jobs.contracts import JOB_SCHEMA_VERSION, JobStatus


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    """Durable control-plane record. Payload content never belongs in this table."""

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="ck_jobs_progress"),
        CheckConstraint("attempt >= 0", name="ck_jobs_attempt"),
        CheckConstraint("max_attempts >= 1", name="ck_jobs_max_attempts"),
        CheckConstraint("timeout_seconds >= 1", name="ck_jobs_timeout_seconds"),
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','RETRY_SCHEDULED',"
            "'CANCELLATION_REQUESTED','CANCELLED','TIMED_OUT')",
            name="ck_jobs_status",
        ),
        UniqueConstraint(
            "owner_id", "job_type", "idempotency_key", name="uq_jobs_idempotency_scope"
        ),
        Index("ix_jobs_owner_status_created", "owner_id", "status", "created_at"),
        Index("ix_jobs_project_status_created", "project_id", "status", "created_at"),
        Index("ix_jobs_status_available", "status", "available_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    schema_version: Mapped[str] = mapped_column(
        String(32), nullable=False, default=JOB_SCHEMA_VERSION
    )
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=JobStatus.QUEUED.value
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=900)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    available_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancel_requested_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(nullable=True)
