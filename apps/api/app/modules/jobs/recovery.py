from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.modules.jobs.contracts import JobQueueMessage, JobStatus
from app.modules.jobs.models import Job
from app.modules.jobs.queue import JobQueue
from app.modules.jobs.repository import InvalidJobTransitionError, JobRepository


@dataclass(frozen=True, slots=True)
class RecoveryReport:
    inspected: int = 0
    requeued: int = 0
    cancelled: int = 0
    exhausted: int = 0
    active: int = 0


class JobRecoveryReconciler:
    """Rebuild Redis transport state from the durable PostgreSQL control plane."""

    def __init__(self, repository: JobRepository, queue: JobQueue) -> None:
        self._repository = repository
        self._queue = queue

    def reconcile(self) -> RecoveryReport:
        abandoned = set(self._queue.recover_abandoned())
        now = datetime.now(timezone.utc)
        counts = {"requeued": 0, "cancelled": 0, "exhausted": 0, "active": 0}
        jobs = self._repository.list_recoverable()
        for stale in jobs:
            job = self._repository.get(stale.id)
            if job is None:
                continue
            status = JobStatus(job.status)
            try:
                if status is JobStatus.CANCELLATION_REQUESTED:
                    self._repository.transition(
                        job.id,
                        {JobStatus.CANCELLATION_REQUESTED},
                        JobStatus.CANCELLED,
                        error_code="JOB_CANCELLED",
                        error_message="Job cancellation was preserved during recovery",
                        cancelled_at=now,
                        completed_at=now,
                    )
                    counts["cancelled"] += 1
                    continue
                if status is JobStatus.RUNNING:
                    if self._queue.has_active_lease(job.id):
                        counts["active"] += 1
                        continue
                    if job.attempt >= job.max_attempts:
                        self._repository.transition(
                            job.id,
                            {JobStatus.RUNNING},
                            JobStatus.FAILED,
                            error_code="JOB_RETRY_EXHAUSTED",
                            error_message="Job recovery exhausted the configured attempt limit",
                            completed_at=now,
                        )
                        counts["exhausted"] += 1
                        continue
                    job = self._repository.transition(
                        job.id,
                        {JobStatus.RUNNING},
                        JobStatus.QUEUED,
                        error_code="JOB_LEASE_LOST",
                        error_message="Worker lease was lost; job recovered for another attempt",
                        available_at=now,
                        progress=0,
                    )
                elif status is JobStatus.RETRY_SCHEDULED:
                    available_at = job.available_at
                    if available_at.tzinfo is None:
                        available_at = available_at.replace(tzinfo=timezone.utc)
                    delay = max((available_at - now).total_seconds(), 0)
                    if delay > 0:
                        self._queue.enqueue(self._message(job), delay)
                        counts["active"] += 1
                        continue
                    job = self._repository.transition(
                        job.id,
                        {JobStatus.RETRY_SCHEDULED},
                        JobStatus.QUEUED,
                        available_at=now,
                        progress=0,
                    )
                scheduled = self._queue.enqueue(self._message(job))
                if scheduled or job.id in abandoned:
                    counts["requeued"] += 1
            except InvalidJobTransitionError:
                # Another reconciler won the compare-and-set race.
                continue
        return RecoveryReport(inspected=len(jobs), **counts)

    @staticmethod
    def _message(job: Job) -> JobQueueMessage:
        return JobQueueMessage(
            job_id=job.id,
            job_type=job.job_type,
            request_id=job.request_id,
            correlation_id=job.correlation_id,
        )
