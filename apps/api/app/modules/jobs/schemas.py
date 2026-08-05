from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.jobs.contracts import JOB_SCHEMA_VERSION, JobStatus, JobType


class JobCreateRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    schema_version: str = JOB_SCHEMA_VERSION
    job_type: JobType
    status: JobStatus
    project_id: str
    resource_id: str
    progress: int
    attempt: int
    max_attempts: int
    timeout_seconds: int
    request_id: str | None
    correlation_id: str | None
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancel_requested_at: datetime | None
    cancelled_at: datetime | None
