from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.engineering.level2_schemas import Level2VerificationEvidence
from app.modules.engineering.manufacturing_schemas import ManufacturingGeometryModel
from app.modules.engineering.postprocessor_schemas import GCodeCandidate
from app.modules.engineering.toolpath_schemas import ToolpathCandidate


class HumanReviewEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer_ref: str = Field(min_length=1, max_length=255)
    decision: Literal["APPROVED_FOR_CONTROLLED_VALIDATION", "REJECTED"]
    evidence_ref: str = Field(min_length=1, max_length=500)


class ControlledBlindValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    holdout_id: str = Field(min_length=1, max_length=255)
    sealed_reference_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    cad_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    manufacturing_model: ManufacturingGeometryModel
    toolpath: ToolpathCandidate
    gcode_candidate: GCodeCandidate
    level2_evidence: Level2VerificationEvidence
    questions_asked: list[str] = Field(default_factory=list)
    human_review: HumanReviewEvidence | None = None


class GateEvidence(BaseModel):
    gate: Literal["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]
    status: Literal["PASS", "FAIL", "PENDING_REVIEW"]
    evidence_ref: str


class ControlledBlindValidationEvidence(BaseModel):
    schema_version: str = "vena-ia.controlled-blind-validation/v1"
    holdout_id: str
    sealed_reference_hash: str
    frozen_artifact_hashes: dict[str, str]
    frozen_bundle_hash: str
    gates: list[GateEvidence]
    questions_asked: list[str]
    omissions: list[str]
    false_positives: list[str]
    process_divergence: str
    toolpath_divergence: str
    human_adjudication: str
    replay_hash: str
    cad_to_gcode_controlled_validation_ready: bool = False
    physical_use_authorized: bool = False
    limitations: list[str]
