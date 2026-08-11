from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue


ArtifactType = Literal[
    "CAD",
    "TOPOLOGY_EVIDENCE",
    "MANUFACTURING_GEOMETRY",
    "VERIFIED_PROCESS_PLAN",
    "TOOLPATH_CANDIDATE",
    "GCODE_CANDIDATE",
    "VERIFICATION_EVIDENCE",
    "REVIEW_STATE",
    "REPORT",
]


class DigitalThreadArtifactInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    artifact_id: str = Field(min_length=1, max_length=255)
    artifact_type: ArtifactType
    schema_version: str = Field(min_length=1, max_length=255)
    content: dict[str, JsonValue]
    declared_content_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    upstream_artifact_refs: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    generation_metadata: dict[str, JsonValue] = Field(default_factory=dict)
    verification_refs: tuple[str, ...] = ()
    lifecycle_status: Literal["CURRENT", "STALE", "REVOKED"] = "CURRENT"


class DigitalThreadBuildRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    artifacts: tuple[DigitalThreadArtifactInput, ...]


class DigitalThreadArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    artifact_id: str
    artifact_type: ArtifactType
    schema_version: str
    content_hash: str
    organization_id: str
    lifecycle_status: Literal["CURRENT"] = "CURRENT"
    upstream_artifact_refs: tuple[str, ...]
    downstream_artifact_refs: tuple[str, ...]
    provenance: tuple[str, ...]
    generation_metadata: dict[str, JsonValue]
    replay_metadata: dict[str, str]
    verification_refs: tuple[str, ...]
    review_state_ref: str = "PENDING_AUTHORITATIVE_REVIEW"
    limitations: tuple[str, ...]


class DigitalThreadManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: str = "vena-ia.digital-thread/v1"
    thread_id: str
    organization_id: str
    status: Literal["COMPLETE_NON_PRODUCTION", "INCOMPLETE_REQUIRES_EVIDENCE"]
    artifacts: tuple[DigitalThreadArtifact, ...]
    missing_artifact_types: tuple[ArtifactType, ...]
    replay_hash: str
    g9_state: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    cad_to_gcode_controlled_validation_ready: bool = False
    physical_use_authorized: bool = False
    limitations: tuple[str, ...]


class BoundedIntelligenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    thread: DigitalThreadManifest
    mode: Literal["EXPLAIN", "SUMMARIZE", "IDENTIFY_MISSING", "COMPARE"]
    baseline: DigitalThreadManifest | None = None


class BoundedIntelligenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: str = "vena-ia.bounded-manufacturing-intelligence/v1"
    status: Literal["AVAILABLE_FOR_HUMAN_REVIEW", "BLOCKED_INVALID_EVIDENCE"]
    explanation: str
    findings: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    suggestions: tuple[str, ...]
    read_only: bool = True
    deterministic_evidence_mutated: bool = False
    g9_state: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    physical_use_authorized: bool = False
    limitations: tuple[str, ...]
