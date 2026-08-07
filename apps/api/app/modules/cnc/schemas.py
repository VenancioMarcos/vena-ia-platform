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
    schema_version: str = "vena-ia.cnc-neutral-plan/v1"
    source_planning_reference: str | None = None
    source_recommendation_reference: str | None = None
    controller_family: str
    machine_profile: str
    operation: CNCOperationType
    parameters: dict[str, float | int]
    operation_candidates: list[dict[str, object]] = Field(default_factory=list)
    machine_neutral_assumptions: list[str] = Field(default_factory=list)
    validation_checks: list[str]
    status: str
    warnings: list[str] = Field(default_factory=list)
    traceability: list[str] = Field(default_factory=list)
    review_status: str = "REQUIRES_HUMAN_REVIEW"
    simulation_only: bool = True
    executable_output: bool = False
    limitations: list[str]
