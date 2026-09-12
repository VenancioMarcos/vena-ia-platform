from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CadJobState = Literal["QUEUED", "PROCESSING", "COMPLETED", "FAILED"]


class StepUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    filename: str
    size_bytes: int
    schema_type: str
    status: CadJobState


class CadProfilePoint(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    r_mm: float = Field(ge=0)
    z_mm: float


class CadProfileBoundingBox(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    max_radius_mm: float = Field(ge=0)
    min_z_mm: float
    max_z_mm: float
    total_z_length_mm: float = Field(ge=0)


class CadProfileData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: tuple[CadProfilePoint, ...]
    bounding_box: CadProfileBoundingBox
    review_status: Literal["PROFILE_AVAILABLE_REQUIRES_REVIEW"]
    warnings: tuple[str, ...] = ()


class CadJobStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: CadJobState
    error_detail: str | None = None
    profile_data: CadProfileData | None = None
