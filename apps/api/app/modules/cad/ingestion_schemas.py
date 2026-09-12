from typing import Literal

from pydantic import BaseModel, ConfigDict


CadJobState = Literal["QUEUED", "PROCESSING", "COMPLETED", "FAILED"]


class StepUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    filename: str
    size_bytes: int
    schema_type: str
    status: CadJobState


class CadJobStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: CadJobState
    error_detail: str | None = None
