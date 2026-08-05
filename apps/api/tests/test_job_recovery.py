from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from app.modules.jobs.contracts import JobQueueMessage, JobStatus
from app.modules.jobs.queue import JobQueueUnavailable, MemoryJobQueue
from app.modules.jobs.recovery import JobRecoveryReconciler
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.worker import JobWorker, SafeJobExecutionError
from conftest import TestingSessionLocal
from test_jobs import _seed_job


def _reconcile(db: Session, queue: MemoryJobQueue):
    return JobRecoveryReconciler(JobRepository(db), queue).reconcile()


def test_running_job_with_expired_lease_is_recovered(db_session: Session) -> None:
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    job = _seed_job(db_session)
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    assert queue.claim("interrupted", 5) is not None
    JobRepository(db_session).transition(
        job.id, {JobStatus.QUEUED}, JobStatus.RUNNING, attempt=1, progress=70
    )
    now[0] = 16

    report = _reconcile(db_session, queue)

    db_session.expire_all()
    stored = db_session.get(type(job), job.id)
    assert report.requeued == 1
    assert stored is not None and stored.status == JobStatus.QUEUED.value
    assert stored.progress == 0 and stored.error_code == "JOB_LEASE_LOST"
    assert queue.claim("replacement", 5) is not None


def test_running_job_with_valid_lease_is_not_recovered(db_session: Session) -> None:
    queue = MemoryJobQueue()
    job = _seed_job(db_session)
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    assert queue.claim("active", 60) is not None
    JobRepository(db_session).transition(job.id, {JobStatus.QUEUED}, JobStatus.RUNNING, attempt=1)

    report = _reconcile(db_session, queue)

    assert report.active == 1 and report.requeued == 0
    assert queue.claim("other", 60) is None


def test_redis_state_loss_is_rebuilt_from_postgresql(db_session: Session) -> None:
    job = _seed_job(db_session)
    replacement_queue = MemoryJobQueue()

    report = _reconcile(db_session, replacement_queue)

    assert report.requeued == 1
    claim = replacement_queue.claim("replacement", 30)
    assert claim is not None and claim.message.job_id == job.id


def test_due_retry_and_cancellation_survive_restart(db_session: Session) -> None:
    retry_job = _seed_job(db_session, status=JobStatus.RETRY_SCHEDULED)
    retry_job.available_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    cancelled_job = _seed_job(db_session, status=JobStatus.CANCELLATION_REQUESTED)
    db_session.commit()
    queue = MemoryJobQueue()

    report = _reconcile(db_session, queue)

    db_session.expire_all()
    assert report.requeued == 1 and report.cancelled == 1
    assert db_session.get(type(retry_job), retry_job.id).status == JobStatus.QUEUED.value
    cancelled = db_session.get(type(cancelled_job), cancelled_job.id)
    assert cancelled.status == JobStatus.CANCELLED.value
    assert cancelled.error_code == "JOB_CANCELLED"


def test_recovery_respects_max_attempts(db_session: Session) -> None:
    job = _seed_job(db_session, status=JobStatus.RUNNING, max_attempts=1)
    job.attempt = 1
    db_session.commit()

    report = _reconcile(db_session, MemoryJobQueue())

    db_session.expire_all()
    stored = db_session.get(type(job), job.id)
    assert report.exhausted == 1
    assert stored.status == JobStatus.FAILED.value
    assert stored.error_code == "JOB_RETRY_EXHAUSTED"


def test_repeated_acknowledge_is_idempotent_but_wrong_owner_is_rejected() -> None:
    queue = MemoryJobQueue()
    message = JobQueueMessage("job-1", "document.processing")
    queue.enqueue(message)
    assert queue.claim("owner", 30) is not None
    queue.acknowledge(message.job_id, "owner")
    queue.acknowledge(message.job_id, "owner")


def test_safe_non_retryable_failure_is_terminal(db_session: Session) -> None:
    job = _seed_job(db_session)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))

    def missing(_job, _progress, _cancelled):
        raise SafeJobExecutionError(
            "RESOURCE_NOT_FOUND", "Job resource is unavailable", retryable=False
        )

    result = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: missing},
        worker_id="worker",
        lease_seconds=30,
        retry_base_seconds=1,
    ).run_once()

    db_session.expire_all()
    stored = db_session.get(type(job), job.id)
    assert result.outcome == "failed"
    assert stored.status == JobStatus.FAILED.value
    assert stored.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.parametrize("code", ["DEPENDENCY_UNAVAILABLE", "JOB_LEASE_LOST"])
def test_safe_retryable_failures_keep_identity(db_session: Session, code: str) -> None:
    job = _seed_job(db_session, max_attempts=2)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))

    def unavailable(_job, _progress, _cancelled):
        raise SafeJobExecutionError(code, "Dependency is temporarily unavailable", retryable=True)

    result = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: unavailable},
        worker_id="worker",
        lease_seconds=30,
        retry_base_seconds=1,
    ).run_once()

    db_session.expire_all()
    stored = db_session.get(type(job), job.id)
    assert result.outcome == "retry_scheduled"
    assert stored.id == job.id and stored.status == JobStatus.RETRY_SCHEDULED.value
    assert stored.error_code == code


def test_worker_handles_postgresql_unavailability_without_claiming() -> None:
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage("job", "document.processing"))

    def unavailable_session():
        raise RuntimeError("postgresql unavailable")

    result = JobWorker(
        unavailable_session,
        queue,
        {},
        worker_id="worker",
        lease_seconds=30,
        retry_base_seconds=1,
    ).run_once()

    assert result.outcome == "dependency_unavailable"
    assert queue.claim("replacement", 30) is not None


def test_lease_loss_during_progress_schedules_safe_retry(db_session: Session) -> None:
    class LeaseLossQueue(MemoryJobQueue):
        calls = 0

        def extend_lease(self, job_id: str, worker_id: str, lease_seconds: int) -> None:
            self.calls += 1
            if self.calls > 1:
                raise JobQueueUnavailable("redis unavailable")
            super().extend_lease(job_id, worker_id, lease_seconds)

    job = _seed_job(db_session, max_attempts=2)
    queue = LeaseLossQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: lambda _job, progress, _cancelled: progress(50)},
        worker_id="worker",
        lease_seconds=30,
        retry_base_seconds=1,
    )

    assert worker.run_once().outcome == "retry_scheduled"
    db_session.expire_all()
    stored = db_session.get(type(job), job.id)
    assert stored.status == JobStatus.RETRY_SCHEDULED.value
    assert stored.error_code == "JOB_LEASE_LOST"
