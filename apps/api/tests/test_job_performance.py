import time

from app.modules.jobs.contracts import JobQueueMessage, JobType
from app.modules.jobs.queue import MemoryJobQueue


def test_synthetic_queue_lifecycle_budget() -> None:
    """Detect gross algorithmic regressions; this is not a production capacity SLO."""

    queue = MemoryJobQueue()
    messages = [
        JobQueueMessage(f"00000000-0000-0000-0000-{index:012d}", JobType.DOCUMENT_PROCESSING)
        for index in range(1_000)
    ]
    started = time.perf_counter()
    for message in messages:
        queue.enqueue(message)
    for message in messages:
        claimed = queue.claim("synthetic-worker", 30)
        assert claimed is not None and claimed.message.job_id == message.job_id
        queue.acknowledge(message.job_id, "synthetic-worker")
    duration = time.perf_counter() - started

    assert duration < 2.0


def test_synthetic_retry_and_cancel_queue_primitives() -> None:
    now = [0.0]
    queue = MemoryJobQueue(lambda: now[0])
    message = JobQueueMessage(
        "00000000-0000-0000-0000-000000000001",
        JobType.DOCUMENT_PROCESSING,
    )
    queue.enqueue(message)
    assert queue.claim("synthetic-worker", 5) is not None
    queue.retry(message, "synthetic-worker", 1)
    now[0] = 1
    assert queue.claim("synthetic-worker", 5) is not None
    queue.acknowledge(message.job_id, "synthetic-worker")
