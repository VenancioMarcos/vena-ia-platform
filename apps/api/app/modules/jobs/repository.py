from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.jobs.contracts import ALLOWED_TRANSITIONS, JobStatus
from app.modules.jobs.models import Job


class InvalidJobTransitionError(RuntimeError):
    pass


class JobRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, job_id: str) -> Job | None:
        return self._db.get(Job, job_id)

    def get_idempotent(self, owner_id: str, job_type: str, key: str) -> Job | None:
        return self._db.scalar(
            select(Job).where(
                Job.owner_id == owner_id,
                Job.job_type == job_type,
                Job.idempotency_key == key,
            )
        )

    def list_recoverable(self) -> list[Job]:
        return list(
            self._db.scalars(
                select(Job)
                .where(
                    Job.status.in_(
                        [
                            JobStatus.QUEUED.value,
                            JobStatus.RUNNING.value,
                            JobStatus.RETRY_SCHEDULED.value,
                            JobStatus.CANCELLATION_REQUESTED.value,
                        ]
                    )
                )
                .order_by(Job.created_at, Job.id)
            )
        )

    def create(self, job: Job) -> tuple[Job, bool]:
        existing = self.get_idempotent(job.owner_id, job.job_type, job.idempotency_key)
        if existing is not None:
            return existing, False
        try:
            self._db.add(job)
            self._db.commit()
            self._db.refresh(job)
            return job, True
        except IntegrityError:
            self._db.rollback()
            existing = self.get_idempotent(job.owner_id, job.job_type, job.idempotency_key)
            if existing is not None:
                return existing, False
            raise

    def transition(
        self,
        job_id: str,
        expected: set[JobStatus],
        target: JobStatus,
        **values: object,
    ) -> Job:
        if any(target not in ALLOWED_TRANSITIONS[source] for source in expected):
            raise InvalidJobTransitionError(f"Invalid job transition to {target.value}")
        now = datetime.now(timezone.utc)
        fields: dict[str, object] = {"status": target.value, "updated_at": now, **values}
        result = self._db.execute(
            update(Job)
            .where(Job.id == job_id, Job.status.in_([state.value for state in expected]))
            .values(**fields)
        )
        if not isinstance(result, CursorResult) or result.rowcount != 1:
            self._db.rollback()
            current = self.get(job_id)
            state = current.status if current is not None else "missing"
            raise InvalidJobTransitionError(
                f"Job {job_id} cannot transition from {state} to {target.value}"
            )
        self._db.commit()
        job = self.get(job_id)
        assert job is not None
        self._db.refresh(job)
        return job

    def update_progress(self, job_id: str, progress: int) -> Job:
        progress = max(0, min(100, progress))
        now = datetime.now(timezone.utc)
        result = self._db.execute(
            update(Job)
            .where(
                Job.id == job_id,
                Job.status.in_([JobStatus.RUNNING.value, JobStatus.CANCELLATION_REQUESTED.value]),
                Job.progress <= progress,
            )
            .values(progress=progress, updated_at=now)
        )
        if not isinstance(result, CursorResult) or result.rowcount != 1:
            self._db.rollback()
            raise InvalidJobTransitionError("Progress update rejected")
        self._db.commit()
        job = self.get(job_id)
        assert job is not None
        self._db.refresh(job)
        return job
