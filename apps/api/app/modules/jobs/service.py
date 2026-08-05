from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from app.modules.documents.service import DocumentService
from app.modules.jobs.contracts import JobQueueMessage, JobStatus, JobType
from app.modules.jobs.models import Job
from app.modules.jobs.queue import JobQueue
from app.modules.jobs.repository import InvalidJobTransitionError, JobRepository
from app.modules.users.models import User


class JobNotFoundError(LookupError):
    pass


class JobIdempotencyConflictError(RuntimeError):
    pass


class JobService:
    def __init__(
        self,
        repository: JobRepository,
        queue: JobQueue,
        current_user: User,
        document_service: DocumentService,
        *,
        max_attempts: int,
        timeout_seconds: int,
    ) -> None:
        self._repository = repository
        self._queue = queue
        self._user = current_user
        self._documents = document_service
        self._max_attempts = max_attempts
        self._timeout_seconds = timeout_seconds

    @staticmethod
    def _safe_key(key: str) -> str:
        # Persist a one-way digest so operator-selected keys cannot expose PII.
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def create_document_processing(
        self,
        document_id: str,
        idempotency_key: str,
        request_id: str | None,
        correlation_id: str | None,
    ) -> tuple[Job, bool]:
        document = self._documents.get(document_id)
        safe_key = self._safe_key(idempotency_key)
        existing = self._repository.get_idempotent(
            self._user.id, JobType.DOCUMENT_PROCESSING.value, safe_key
        )
        if existing is not None:
            if existing.resource_id != document_id or existing.project_id != document.project_id:
                raise JobIdempotencyConflictError(
                    "Idempotency key is already bound to a different resource"
                )
            if existing.status == JobStatus.QUEUED.value:
                self._queue.enqueue(self._message(existing))
            return existing, False
        job = Job(
            job_type=JobType.DOCUMENT_PROCESSING.value,
            owner_id=self._user.id,
            project_id=document.project_id,
            resource_id=document.id,
            idempotency_key=safe_key,
            request_id=request_id,
            correlation_id=correlation_id,
            max_attempts=self._max_attempts,
            timeout_seconds=self._timeout_seconds,
        )
        job, created = self._repository.create(job)
        if not created and (
            job.resource_id != document_id or job.project_id != document.project_id
        ):
            raise JobIdempotencyConflictError(
                "Idempotency key is already bound to a different resource"
            )
        if created or job.status == JobStatus.QUEUED.value:
            self._queue.enqueue(self._message(job))
        return job, created

    def get(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        if job is None or job.owner_id != self._user.id:
            raise JobNotFoundError("Job not found")
        return job

    def cancel(self, job_id: str) -> Job:
        job = self.get(job_id)
        current = JobStatus(job.status)
        if current in {JobStatus.QUEUED, JobStatus.RETRY_SCHEDULED}:
            return self._repository.transition(
                job.id,
                {current},
                JobStatus.CANCELLED,
                cancel_requested_at=datetime.now(timezone.utc),
                cancelled_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
        if current is JobStatus.RUNNING:
            return self._repository.transition(
                job.id,
                {JobStatus.RUNNING},
                JobStatus.CANCELLATION_REQUESTED,
                cancel_requested_at=datetime.now(timezone.utc),
            )
        if current is JobStatus.CANCELLATION_REQUESTED:
            return job
        raise InvalidJobTransitionError(f"Job in {current.value} cannot be cancelled")

    def retry(self, job_id: str) -> Job:
        job = self.get(job_id)
        current = JobStatus(job.status)
        if current not in {JobStatus.FAILED, JobStatus.TIMED_OUT}:
            raise InvalidJobTransitionError(f"Job in {current.value} cannot be retried")
        if job.attempt >= job.max_attempts:
            raise InvalidJobTransitionError("Job retry limit is exhausted")
        queued = self._repository.transition(
            job.id,
            {current},
            JobStatus.QUEUED,
            error_code=None,
            error_message=None,
            completed_at=None,
            progress=0,
            available_at=datetime.now(timezone.utc),
        )
        self._queue.enqueue(self._message(queued))
        return queued

    @staticmethod
    def _message(job: Job) -> JobQueueMessage:
        return JobQueueMessage(
            job_id=job.id,
            job_type=job.job_type,
            request_id=job.request_id,
            correlation_id=job.correlation_id,
        )


class WorkerJobService:
    """Worker-side transitions with compare-and-set persistence semantics."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    def start(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        if job is None:
            raise JobNotFoundError("Job not found")
        if job.status == JobStatus.RETRY_SCHEDULED.value:
            job = self._repository.transition(
                job_id,
                {JobStatus.RETRY_SCHEDULED},
                JobStatus.QUEUED,
                available_at=datetime.now(timezone.utc),
                progress=0,
            )
        return self._repository.transition(
            job_id,
            {JobStatus.QUEUED},
            JobStatus.RUNNING,
            attempt=job.attempt + 1,
            started_at=datetime.now(timezone.utc),
            progress=1,
        )

    def progress(self, job_id: str, value: int) -> Job:
        return self._repository.update_progress(job_id, value)

    def succeed(self, job_id: str) -> Job:
        return self._repository.transition(
            job_id,
            {JobStatus.RUNNING},
            JobStatus.SUCCEEDED,
            progress=100,
            completed_at=datetime.now(timezone.utc),
            error_code=None,
            error_message=None,
        )

    def cancel_if_requested(self, job_id: str) -> bool:
        job = self._repository.get(job_id)
        if job is None or job.status != JobStatus.CANCELLATION_REQUESTED.value:
            return False
        self._repository.transition(
            job_id,
            {JobStatus.CANCELLATION_REQUESTED},
            JobStatus.CANCELLED,
            cancelled_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        return True

    def fail(self, job_id: str, code: str, message: str, retry_delay: float) -> Job:
        job = self._repository.get(job_id)
        if job is None:
            raise JobNotFoundError("Job not found")
        safe_message = message[:500]
        if job.attempt < job.max_attempts:
            return self._repository.transition(
                job_id,
                {JobStatus.RUNNING},
                JobStatus.RETRY_SCHEDULED,
                error_code=code[:64],
                error_message=safe_message,
                available_at=datetime.now(timezone.utc) + timedelta(seconds=retry_delay),
            )
        return self._repository.transition(
            job_id,
            {JobStatus.RUNNING},
            JobStatus.FAILED,
            error_code=code[:64],
            error_message=safe_message,
            completed_at=datetime.now(timezone.utc),
        )

    def time_out(self, job_id: str) -> Job:
        return self._repository.transition(
            job_id,
            {JobStatus.RUNNING, JobStatus.CANCELLATION_REQUESTED},
            JobStatus.TIMED_OUT,
            error_code="JOB_TIMEOUT",
            error_message="Job exceeded its execution time limit",
            completed_at=datetime.now(timezone.utc),
        )

    def fail_terminal(self, job_id: str, code: str, message: str) -> Job:
        return self._repository.transition(
            job_id,
            {JobStatus.RUNNING},
            JobStatus.FAILED,
            error_code=code[:64],
            error_message=message[:500],
            completed_at=datetime.now(timezone.utc),
        )
