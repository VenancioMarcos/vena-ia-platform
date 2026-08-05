import json
import statistics
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
    samples_ms: list[float] = []
    for message in messages:
        operation_started = time.perf_counter()
        queue.enqueue(message)
        samples_ms.append((time.perf_counter() - operation_started) * 1_000)
    for message in messages:
        operation_started = time.perf_counter()
        claimed = queue.claim("synthetic-worker", 30)
        assert claimed is not None and claimed.message.job_id == message.job_id
        queue.acknowledge(message.job_id, "synthetic-worker")
        samples_ms.append((time.perf_counter() - operation_started) * 1_000)
    duration = time.perf_counter() - started

    ordered = sorted(samples_ms)
    report = {
        "schema_version": "vena-ia.job-performance/v1",
        "environment": "in-process-memory-queue-synthetic",
        "operations": len(samples_ms),
        "duration_ms": round(duration * 1_000, 3),
        "average_ms": round(statistics.fmean(samples_ms), 6),
        "p50_ms": round(statistics.median(samples_ms), 6),
        "p95_ms": round(ordered[int(len(ordered) * 0.95) - 1], 6),
        "p99_ms": round(ordered[int(len(ordered) * 0.99) - 1], 6),
        "limitation": "synthetic local evidence; not capacity, SLA, or SLO",
    }
    print("JOB_PERFORMANCE_METRICS " + json.dumps(report, sort_keys=True))

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
