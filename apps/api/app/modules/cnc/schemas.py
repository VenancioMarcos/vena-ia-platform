from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class CNCOperationType(StrEnum):
    FACE_MILLING = "FACE_MILLING"
    CONTOUR_MILLING = "CONTOUR_MILLING"
    DRILLING = "DRILLING"


class CNCPlanRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    operation: CNCOperationType
    tool_number: int = Field(ge=1, le=999)
    spindle_rpm: float = Field(gt=0, le=30_000)
    feed_mm_min: float = Field(gt=0, le=30_000)
    clearance_z_mm: float = Field(gt=0, le=1_000)


class CNCPlanPreview(BaseModel):
    controller_family: str
    machine_profile: str
    operation: CNCOperationType
    parameters: dict[str, float | int]
    validation_checks: list[str]
    status: str
    executable_output: bool
    limitations: list[str]
