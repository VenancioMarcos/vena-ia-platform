from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.engineering.blind_validation_schemas import GateEvidence


class G9ReviewPackage(BaseModel):
    """Deterministic read-only handoff; never a review decision or authority record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["vena-ia.g9-review-package/v1"] = (
        "vena-ia.g9-review-package/v1"
    )
    package_id: str = Field(pattern=r"^g9-package-[0-9a-f]{24}$")
    package_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    organization_id: str
    candidate_output_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    digital_thread_id: str
    digital_thread_replay_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    blind_validation_bundle_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    blind_validation_replay_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_hashes: dict[str, str]
    contract_versions: dict[str, str]
    component_versions: dict[str, str]
    gates: tuple[GateEvidence, ...]
    level1_status: Literal["PASS_REQUIRES_HUMAN_REVIEW"]
    level1_replay_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    level2_status: Literal["PASS_REQUIRES_HUMAN_REVIEW"]
    level2_replay_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    classification: Literal["CANDIDATE_FOR_VALIDATION"] = "CANDIDATE_FOR_VALIDATION"
    evidence_lifecycle: Literal["CURRENT"] = "CURRENT"
    g9_state: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    known_limitations: tuple[str, ...]
    unresolved_risks: tuple[Literal["R-049", "R-050", "R-051", "R-052"], ...]
    human_review_protocol: tuple[str, ...]
    external_validation_protocol: tuple[str, ...]
    required_external_artifacts: tuple[str, ...]
    automatic_authority: Literal[False] = False
    physical_use_authorized: Literal[False] = False
    machine_send: Literal[False] = False
    dnc: Literal[False] = False
    nc_transfer: Literal[False] = False
    cycle_start: Literal[False] = False
    direct_machine_control: Literal[False] = False
    human_review_bypass: Literal[False] = False
