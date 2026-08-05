from __future__ import annotations

from collections.abc import Generator
import os
import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session
from redis import Redis

from app.main import app
from app.modules.documents.dependencies import get_document_storage
from app.modules.jobs.contracts import JOB_SCHEMA_VERSION, JobQueueMessage, JobStatus, JobType
from app.modules.jobs.models import Job
from app.modules.jobs.queue import (
    InvalidJobQueueMessage,
    JobQueueUnavailable,
    MemoryJobQueue,
    RedisJobQueue,
)
from app.modules.jobs.repository import InvalidJobTransitionError, JobRepository
from app.modules.jobs.worker import JobWorker
from app.modules.projects.models import Project
from conftest import TestingSessionLocal

PDF_BYTES = b"%PDF-1.7\nfixture\n%%EOF"


@pytest.fixture()
def storage() -> Generator[MagicMock, None, None]:
    value = MagicMock()
    app.dependency_overrides[get_document_storage] = lambda: value
    yield value
    app.dependency_overrides.pop(get_document_storage, None)


def _project_and_document(client, make_account, storage, email: str = "jobs@vena-ia.dev"):
    owner = make_account(email)
    project = client.post(
        "/projects", headers=owner.headers, json={"name": "Async Jobs"}
    ).json()
    document = client.post(
        f"/projects/{project['id']}/documents",
        headers=owner.headers,
        files={"file": ("manual.pdf", PDF_BYTES, "application/pdf")},
    ).json()
    return owner, project, document


def test_creates_idempotent_document_job(client, make_account, storage) -> None:
    owner, project, document = _project_and_document(client, make_account, storage)
    payload = {"idempotency_key": "upload:manual:001"}

    first = client.post(
        f"/documents/{document['id']}/jobs/processing",
        headers=owner.headers,
        json=payload,
    )
    second = client.post(
        f"/documents/{document['id']}/jobs/processing",
        headers=owner.headers,
        json=payload,
    )

    assert first.status_code == 202
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert first.json() | {"created_at": None, "updated_at": None}  # response is structured
    assert first.json()["schema_version"] == JOB_SCHEMA_VERSION
    assert first.json()["project_id"] == project["id"]
    assert first.json()["status"] == "QUEUED"
    db = TestingSessionLocal()
    try:
        stored = db.get(Job, first.json()["id"])
        assert stored is not None
        assert stored.idempotency_key != payload["idempotency_key"]
        assert "manual" not in stored.idempotency_key
    finally:
        db.close()


def test_idempotency_key_cannot_be_rebound(client, make_account, storage) -> None:
    owner, project, first_document = _project_and_document(client, make_account, storage)
    second_document = client.post(
        f"/projects/{project['id']}/documents",
        headers=owner.headers,
        files={"file": ("other.pdf", PDF_BYTES, "application/pdf")},
    ).json()
    payload = {"idempotency_key": "same-key-001"}
    first = client.post(
        f"/documents/{first_document['id']}/jobs/processing",
        headers=owner.headers,
        json=payload,
    )
    conflict = client.post(
        f"/documents/{second_document['id']}/jobs/processing",
        headers=owner.headers,
        json=payload,
    )
    assert first.status_code == 202
    assert conflict.status_code == 409


def test_job_access_is_concealed_from_another_user(client, make_account, storage) -> None:
    owner, _project, document = _project_and_document(client, make_account, storage)
    created = client.post(
        f"/documents/{document['id']}/jobs/processing",
        headers=owner.headers,
        json={"idempotency_key": "private-job-001"},
    ).json()
    intruder = make_account("intruder-jobs@vena-ia.dev")
    assert client.get(f"/jobs/{created['id']}", headers=intruder.headers).status_code == 404
    assert client.post(f"/jobs/{created['id']}/cancel", headers=intruder.headers).status_code == 404


def test_cancel_queued_job_is_terminal(client, make_account, storage) -> None:
    owner, _project, document = _project_and_document(client, make_account, storage)
    created = client.post(
        f"/documents/{document['id']}/jobs/processing",
        headers=owner.headers,
        json={"idempotency_key": "cancel-job-001"},
    ).json()
    cancelled = client.post(f"/jobs/{created['id']}/cancel", headers=owner.headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert cancelled.json()["cancelled_at"] is not None


def test_repository_rejects_terminal_state_regression(db_session: Session) -> None:
    job = _seed_job(db_session, status=JobStatus.SUCCEEDED)
    with pytest.raises(InvalidJobTransitionError):
        JobRepository(db_session).transition(
            job.id, {JobStatus.SUCCEEDED}, JobStatus.RUNNING
        )


def test_repository_rejects_decreasing_progress(db_session: Session) -> None:
    job = _seed_job(db_session)
    repository = JobRepository(db_session)
    repository.transition(job.id, {JobStatus.QUEUED}, JobStatus.RUNNING, progress=50)
    with pytest.raises(InvalidJobTransitionError):
        repository.update_progress(job.id, 25)


def test_memory_queue_claim_is_exclusive_and_ack_requires_owner() -> None:
    queue = MemoryJobQueue()
    message = JobQueueMessage("job-1", JobType.DOCUMENT_PROCESSING.value)
    queue.enqueue(message)
    claimed = queue.claim("worker-1", 30)
    assert claimed is not None
    assert queue.claim("worker-2", 30) is None
    with pytest.raises(JobQueueUnavailable):
        queue.acknowledge("job-1", "worker-2")
    queue.acknowledge("job-1", "worker-1")


def test_memory_queue_recovers_expired_lease() -> None:
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    queue.enqueue(JobQueueMessage("job-1", JobType.DOCUMENT_PROCESSING.value))
    assert queue.claim("dead-worker", 5) is not None
    now[0] = 16.0
    assert queue.recover_abandoned() == 1
    claimed = queue.claim("replacement", 5)
    assert claimed is not None and claimed.worker_id == "replacement"


def test_memory_queue_extends_owned_lease() -> None:
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    message = JobQueueMessage("job-1", JobType.DOCUMENT_PROCESSING.value)
    queue.enqueue(message)
    assert queue.claim("worker", 5) is not None
    queue.extend_lease("job-1", "worker", 20)
    now[0] = 16
    assert queue.recover_abandoned() == 0
    now[0] = 31
    assert queue.recover_abandoned() == 1


def test_memory_queue_honors_retry_delay() -> None:
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    message = JobQueueMessage("job-1", JobType.DOCUMENT_PROCESSING.value)
    queue.enqueue(message)
    assert queue.claim("worker", 5) is not None
    queue.retry(message, "worker", 4)
    assert queue.claim("worker", 5) is None
    now[0] = 14.0
    assert queue.claim("worker", 5) is not None


def test_worker_completes_allowlisted_job(db_session: Session) -> None:
    job = _seed_job(db_session)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    seen: list[int] = []

    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: lambda _job, progress, _cancelled: (progress(50), seen.append(1))},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    result = worker.run_once()
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert result.outcome == "succeeded"
    assert seen == [1]
    assert stored is not None and stored.status == JobStatus.SUCCEEDED.value
    assert stored.progress == 100 and stored.attempt == 1


def test_worker_retries_then_fails_without_exposing_exception(db_session: Session) -> None:
    job = _seed_job(db_session, max_attempts=2)
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    queue.enqueue(JobQueueMessage(job.id, job.job_type))

    def fail(_job, _progress, _cancelled):
        raise RuntimeError("secret stack and payload")

    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: fail},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "retry_scheduled"
    now[0] = 11.0
    assert worker.run_once().outcome == "failed"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.status == JobStatus.FAILED.value
    assert stored.attempt == 2
    assert stored.error_code == "JOB_EXECUTION_FAILED"
    assert "secret" not in (stored.error_message or "")


def test_worker_resets_progress_before_retry(db_session: Session) -> None:
    job = _seed_job(db_session, max_attempts=2)
    now = [10.0]
    queue = MemoryJobQueue(lambda: now[0])
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    attempts = [0]

    def flaky(_job, progress, _cancelled) -> None:
        attempts[0] += 1
        progress(80 if attempts[0] == 1 else 10)
        if attempts[0] == 1:
            raise RuntimeError("transient")

    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: flaky},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "retry_scheduled"
    now[0] = 11
    assert worker.run_once().outcome == "succeeded"


def test_worker_honors_running_cancellation(db_session: Session) -> None:
    job = _seed_job(db_session)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))

    def cancel(current: Job, _progress, cancelled) -> None:
        other = TestingSessionLocal()
        try:
            JobRepository(other).transition(
                current.id,
                {JobStatus.RUNNING},
                JobStatus.CANCELLATION_REQUESTED,
            )
        finally:
            other.close()
        assert cancelled()

    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: cancel},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "cancelled"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.status == JobStatus.CANCELLED.value


def test_cancellation_wins_when_handler_also_fails(db_session: Session) -> None:
    job = _seed_job(db_session)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))

    def cancel_then_fail(current: Job, _progress, _cancelled) -> None:
        other = TestingSessionLocal()
        try:
            JobRepository(other).transition(
                current.id,
                {JobStatus.RUNNING},
                JobStatus.CANCELLATION_REQUESTED,
            )
        finally:
            other.close()
        raise RuntimeError("failure after cancellation")

    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: cancel_then_fail},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "cancelled"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.status == JobStatus.CANCELLED.value


def test_worker_marks_elapsed_job_timed_out(db_session: Session) -> None:
    job = _seed_job(db_session, timeout_seconds=1)
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    ticks = iter((0.0, 2.0))
    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: lambda _job, _progress, _cancelled: None},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
        monotonic=lambda: next(ticks),
    )
    assert worker.run_once().outcome == "timed_out"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.status == JobStatus.TIMED_OUT.value
    assert stored.error_code == "JOB_TIMEOUT"


def test_worker_rejects_unallowlisted_type(db_session: Session) -> None:
    job = _seed_job(db_session, job_type="user.shell")
    queue = MemoryJobQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "failed"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.error_code == "JOB_TYPE_NOT_ALLOWED"


def test_terminal_job_survives_queue_ack_failure(db_session: Session) -> None:
    class AckFailureQueue(MemoryJobQueue):
        def acknowledge(self, job_id: str, worker_id: str) -> None:
            del job_id, worker_id
            raise JobQueueUnavailable("redis unavailable")

    job = _seed_job(db_session)
    queue = AckFailureQueue()
    queue.enqueue(JobQueueMessage(job.id, job.job_type))
    worker = JobWorker(
        TestingSessionLocal,
        queue,
        {job.job_type: lambda _job, _progress, _cancelled: None},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "succeeded"
    db_session.expire_all()
    stored = db_session.get(Job, job.id)
    assert stored is not None and stored.status == JobStatus.SUCCEEDED.value


def test_worker_reports_queue_unavailability_without_crashing() -> None:
    class UnavailableQueue(MemoryJobQueue):
        def heartbeat(self, worker_id: str, ttl_seconds: int) -> None:
            del worker_id, ttl_seconds
            raise JobQueueUnavailable("redis unavailable")

    worker = JobWorker(
        TestingSessionLocal,
        UnavailableQueue(),
        {},
        worker_id="worker-1",
        lease_seconds=30,
        retry_base_seconds=1,
    )
    assert worker.run_once().outcome == "queue_unavailable"


@pytest.mark.skipif(
    os.getenv("RUN_REDIS_INTEGRATION") != "1", reason="requires disposable Redis"
)
def test_real_redis_queue_claim_retry_ack_and_recovery() -> None:
    client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    prefix = f"vena_ia:test:jobs:{uuid.uuid4().hex}"
    queue = RedisJobQueue(client, prefix)
    try:
        first = JobQueueMessage(str(uuid.uuid4()), JobType.DOCUMENT_PROCESSING.value)
        queue.enqueue(first)
        claim = queue.claim("worker-a", 5)
        assert claim is not None and claim.message == first
        assert queue.claim("worker-b", 5) is None
        queue.retry(first, "worker-a", 0)
        second_claim = queue.claim("worker-b", 5)
        assert second_claim is not None
        queue.acknowledge(first.job_id, "worker-b")
        assert queue.claim("worker-c", 5) is None

        abandoned = JobQueueMessage(str(uuid.uuid4()), JobType.DOCUMENT_PROCESSING.value)
        queue.enqueue(abandoned)
        assert queue.claim("dead", 5) is not None
        client.zadd(f"{prefix}:leases", {abandoned.job_id: 0})
        assert queue.recover_abandoned() == 1
        assert queue.claim("replacement", 5) is not None

        malformed_id = str(uuid.uuid4())
        client.hset(f"{prefix}:payloads", malformed_id, "not-json")
        client.rpush(f"{prefix}:ready", malformed_id)
        with pytest.raises(InvalidJobQueueMessage):
            queue.claim("validator", 5)
        assert client.hget(f"{prefix}:payloads", malformed_id) is None
    finally:
        keys = list(client.scan_iter(f"{prefix}:*"))
        if keys:
            client.delete(*keys)


def _seed_job(
    db: Session,
    *,
    status: JobStatus = JobStatus.QUEUED,
    max_attempts: int = 3,
    timeout_seconds: int = 900,
    job_type: str = JobType.DOCUMENT_PROCESSING.value,
) -> Job:
    owner_id = "00000000-0000-0000-0000-000000000001"
    project_id = "00000000-0000-0000-0000-000000000002"
    from app.modules.users.models import User

    if db.get(User, owner_id) is None:
        db.add(User(id=owner_id, name="Worker", email="worker@vena-ia.dev"))
        db.add(Project(id=project_id, name="Worker project", owner_id=owner_id))
        db.commit()
    job = Job(
        owner_id=owner_id,
        project_id=project_id,
        resource_id="00000000-0000-0000-0000-000000000003",
        job_type=job_type,
        status=status.value,
        idempotency_key=f"key-{status.value}-{max_attempts}",
        max_attempts=max_attempts,
        timeout_seconds=timeout_seconds,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
