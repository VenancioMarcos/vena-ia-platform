from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

JOB_SCHEMA_VERSION = "vena-ia.job/v1"


class JobType(StrEnum):
    DOCUMENT_PROCESSING = "document.processing"


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    CANCELLATION_REQUESTED = "CANCELLATION_REQUESTED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


TERMINAL_JOB_STATUSES = frozenset(
    {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.TIMED_OUT}
)

ALLOWED_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset(
        {JobStatus.RUNNING, JobStatus.CANCELLATION_REQUESTED, JobStatus.CANCELLED}
    ),
    JobStatus.RUNNING: frozenset(
        {
            JobStatus.QUEUED,
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.RETRY_SCHEDULED,
            JobStatus.CANCELLATION_REQUESTED,
            JobStatus.CANCELLED,
            JobStatus.TIMED_OUT,
        }
    ),
    JobStatus.RETRY_SCHEDULED: frozenset(
        {JobStatus.QUEUED, JobStatus.CANCELLATION_REQUESTED, JobStatus.CANCELLED}
    ),
    JobStatus.CANCELLATION_REQUESTED: frozenset(
        {JobStatus.CANCELLED, JobStatus.FAILED, JobStatus.TIMED_OUT}
    ),
    JobStatus.SUCCEEDED: frozenset(),
    JobStatus.FAILED: frozenset({JobStatus.QUEUED}),
    JobStatus.CANCELLED: frozenset(),
    JobStatus.TIMED_OUT: frozenset({JobStatus.QUEUED}),
}


@dataclass(frozen=True, slots=True)
class JobQueueMessage:
    job_id: str
    job_type: str
    request_id: str | None = None
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class ClaimedJob:
    message: JobQueueMessage
    worker_id: str


SAFE_JOB_ERROR_CODES = frozenset(
    {
        "PDF_ENCRYPTED",
        "PDF_NO_TEXT",
        "PDF_INVALID",
        "RESOURCE_NOT_FOUND",
        "QUEUE_UNAVAILABLE",
        "DEPENDENCY_UNAVAILABLE",
        "JOB_TIMED_OUT",
        "JOB_CANCELLED",
        "JOB_RETRY_EXHAUSTED",
        "JOB_LEASE_LOST",
        "INTERNAL_PROCESSING_ERROR",
        "JOB_TYPE_NOT_ALLOWED",
        "JOB_PAYLOAD_INVALID",
    }
)
