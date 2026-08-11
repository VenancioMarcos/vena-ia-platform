from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.engineering.manufacturing_schemas import ManufacturingGeometryModel


Point3D = tuple[float, float, float]


class ToolGeometry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_id: str = Field(min_length=1, max_length=255)
    diameter_mm: float = Field(gt=0, le=1000)
    flute_length_mm: float = Field(gt=0, le=1000)
    holder_diameter_mm: float | None = Field(default=None, gt=0, le=2000)


class ToolpathCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    manufacturing_model: ManufacturingGeometryModel
    operation_candidate_id: str = Field(min_length=1, max_length=255)
    tool: ToolGeometry
    machine_minimum: Point3D
    machine_maximum: Point3D
    clearance_z_mm: float
    retract_z_mm: float
    feed_mm_min: float = Field(gt=0, le=100_000)

    @model_validator(mode="after")
    def validate_machine_bounds(self) -> "ToolpathCandidateRequest":
        if any(
            self.machine_maximum[index] <= self.machine_minimum[index]
            for index in range(3)
        ):
            raise ValueError("machine_maximum must be greater than machine_minimum")
        if self.clearance_z_mm < self.retract_z_mm:
            raise ValueError("clearance_z_mm must be greater than or equal to retract_z_mm")
        return self


class ToolpathSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    segment_id: str
    primitive: Literal["LINEAR"] = "LINEAR"
    motion: Literal["RAPID_CANDIDATE", "FEED_CANDIDATE"]
    start: Point3D
    end: Point3D
    feed_mm_min: float | None = Field(default=None, gt=0)
    target_region_id: str | None = None


class ToolpathVerificationEvidence(BaseModel):
    schema_version: str = "vena-ia.toolpath-verification-evidence/v1"
    status: Literal["PASS_REQUIRES_HUMAN_REVIEW", "REJECTED"]
    deterministic_replay_hash: str
    checks: list[str]
    rejected_reasons: list[str]
    limitations: list[str]
    physical_validation: bool = False


class ToolpathCandidate(BaseModel):
    schema_version: str = "vena-ia.toolpath-candidate/v1"
    status: Literal["CANDIDATE_FOR_VALIDATION", "REJECTED", "REQUIRES_INPUT"]
    source_manufacturing_model_hash: str
    source_process_plan_hash: str
    operation_candidate_id: str
    tool: ToolGeometry
    machine_bounds: tuple[Point3D, Point3D]
    clearance_z_mm: float
    retract_z_mm: float
    target_region_ids: list[str]
    segments: list[ToolpathSegment]
    limitations: list[str]
    review_state: str = "REQUIRES_HUMAN_REVIEW"
    executable_output: bool = False
    production_authority: bool = False
    verification: ToolpathVerificationEvidence
