from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.modules.engineering.toolpath_schemas import ToolpathCandidate


class GCodeCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    toolpath: ToolpathCandidate


class GCodeVerificationEvidence(BaseModel):
    schema_version: str = "vena-ia.rs274-safe-subset-verification/v1"
    status: Literal["PASS_REQUIRES_HUMAN_REVIEW", "REJECTED"]
    checks: list[str]
    rejected_reasons: list[str]
    replay_hash: str
    physical_validation: bool = False


class GCodeCandidate(BaseModel):
    schema_version: str = "vena-ia.gcode-candidate/v1"
    classification: Literal["CANDIDATE_FOR_VALIDATION"] = "CANDIDATE_FOR_VALIDATION"
    machine_profile: str = "VENA_SYNTHETIC_3AXIS_MILL_V1"
    controller_profile: str = "VENA_RS274_SAFE_SUBSET_V1"
    postprocessor_version: str = "VENA_SYNTHETIC_3AXIS_POST_V1"
    source_toolpath_hash: str
    program: str
    output_hash: str
    manifest: dict[str, str]
    production_authority: bool = False
    human_review: str = "REQUIRED"
    executable_output: bool = False
    verification: GCodeVerificationEvidence
