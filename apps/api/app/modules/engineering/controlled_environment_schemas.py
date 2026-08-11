from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.engineering.blind_validation_schemas import ControlledBlindValidationEvidence
from app.modules.engineering.digital_thread_schemas import DigitalThreadManifest
from app.modules.engineering.g9_review_schemas import G9ReviewPackage
from app.modules.engineering.level2_schemas import KeepOutBounds, Level2VerificationEvidence
from app.modules.engineering.manufacturing_schemas import (
    ManufacturingGeometryModel,
    ManufacturingPlanningRequest,
    Point3D,
)
from app.modules.engineering.postprocessor_schemas import GCodeCandidate
from app.modules.engineering.toolpath_schemas import ToolGeometry, ToolpathCandidate


class ControlledEnvironmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: str = Field(min_length=1, max_length=36)
    planning: ManufacturingPlanningRequest
    tool: ToolGeometry
    machine_minimum: Point3D
    machine_maximum: Point3D
    clearance_z_mm: float
    retract_z_mm: float
    feed_mm_min: float = Field(gt=0, le=100_000)
    fixture_keep_outs: list[KeepOutBounds] = Field(default_factory=list)
    holdout_id: str = Field(min_length=1, max_length=255)
    sealed_reference_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    questions_asked: list[str] = Field(default_factory=list)


class ControlledEnvironmentResult(BaseModel):
    schema_version: Literal["vena-ia.controlled-test-environment/v1"] = (
        "vena-ia.controlled-test-environment/v1"
    )
    status: Literal["READY_FOR_CONTROLLED_DOWNLOAD"]
    manufacturing_model: ManufacturingGeometryModel
    toolpath: ToolpathCandidate
    gcode_candidate: GCodeCandidate
    level2_evidence: Level2VerificationEvidence
    blind_validation: ControlledBlindValidationEvidence
    digital_thread: DigitalThreadManifest
    g9_review_package: G9ReviewPackage
    download_token: str
    classification: Literal["CANDIDATE_FOR_VALIDATION"] = "CANDIDATE_FOR_VALIDATION"
    non_production: Literal[True] = True
    review_state: Literal["REQUIRES_HUMAN_REVIEW"] = "REQUIRES_HUMAN_REVIEW"
    g9_state: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    physical_use_authorized: Literal[False] = False
    machine_send: Literal[False] = False
    dnc: Literal[False] = False
    nc_transfer: Literal[False] = False
    cycle_start: Literal[False] = False
    direct_machine_control: Literal[False] = False
    limitations: list[str]


class ControlledDownloadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: str = Field(min_length=1, max_length=36)
    gcode_candidate: GCodeCandidate
    blind_validation: ControlledBlindValidationEvidence
    digital_thread: DigitalThreadManifest
    download_token: str = Field(min_length=40, max_length=4096)
