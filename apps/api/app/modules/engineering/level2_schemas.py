from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.engineering.manufacturing_schemas import ManufacturingGeometryModel, Point3D
from app.modules.engineering.toolpath_schemas import ToolpathCandidate


class KeepOutBounds(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minimum: Point3D
    maximum: Point3D
    source_ref: str


class Level2VerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    manufacturing_model: ManufacturingGeometryModel
    toolpath: ToolpathCandidate
    fixture_keep_outs: list[KeepOutBounds] = Field(default_factory=list)


class Level2VerificationEvidence(BaseModel):
    schema_version: str = "vena-ia.level2-material-removal-evidence/v1"
    status: Literal["PASS_REQUIRES_HUMAN_REVIEW", "REJECTED", "REQUIRES_INPUT"]
    replay_hash: str
    reconstructed_segment_count: int
    simplified_sweep_volume_mm3: float
    target_coverage: str
    remaining_material: str
    gouge_detected: bool
    protected_surface_violation: bool
    rapid_collision_detected: bool
    fixture_collision_detected: bool | None
    geometric_error: str
    checks: list[str]
    rejected_reasons: list[str]
    limitations: list[str]
    physical_validation: bool = False
