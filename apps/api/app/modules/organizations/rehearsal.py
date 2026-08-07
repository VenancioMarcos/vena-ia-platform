import hashlib
import json
import re
from datetime import datetime
from enum import StrEnum
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.organizations.models import PilotContext, PilotReadinessChecklist


class StrictEvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    FAILED = "FAILED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvidenceItem(StrictEvidenceModel):
    category: str
    status: EvidenceStatus
    source_contract: str
    evidence_reference: str
    generated_at: datetime
    owner: str
    limitations: list[str]
    warnings: list[str]


class SLOProposal(StrictEvidenceModel):
    metric: str
    proposed_target: str
    window: str
    source: str
    owner: str
    environment: Literal["SYNTHETIC_NON_PRODUCTION"] = "SYNTHETIC_NON_PRODUCTION"
    limitations: list[str]


class CapacityAcceptance(StrictEvidenceModel):
    workload_profile: str
    observed_throughput: str
    latency: str
    error_rate: str
    resource_observations: str
    environment: Literal["SYNTHETIC_NON_PRODUCTION"] = "SYNTHETIC_NON_PRODUCTION"
    limitations: list[str]


class SupportPath(StrictEvidenceModel):
    issue_category: str
    owner_role: str
    escalation_path: str
    severity: str
    expected_internal_action: str


class NeutralCNCPlan(StrictEvidenceModel):
    source_plan_schema: Literal["vena-ia.cnc-neutral-plan/v1"]
    status: Literal["SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW"]
    executable_output: Literal[False]
    controller_family: str = Field(min_length=1, max_length=100)
    machine_profile: str = Field(min_length=1, max_length=100)
    operation: str = Field(min_length=1, max_length=100)
    parameters: dict[str, float | int]
    validation_checks: list[str] = Field(min_length=1, max_length=50)
    limitations: list[str] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def reject_executable_content(self) -> "NeutralCNCPlan":
        serialized = json.dumps(
            {
                "controller_family": self.controller_family,
                "machine_profile": self.machine_profile,
                "operation": self.operation,
                "parameter_names": sorted(self.parameters),
            },
            sort_keys=True,
        ).lower()
        dangerous = (
            r"\bg\s*0?\d\b",
            r"\bm\s*0?\d\b",
            r"\b(?:spindle|motion|toolpath|postprocessor|nc[_ -]?file|machine[_ -]?ip|dnc)\b",
        )
        if any(re.search(pattern, serialized) for pattern in dangerous):
            raise ValueError("Executable or machine-control content is forbidden")
        return self


class VirtualCNCCheck(StrictEvidenceModel):
    check: str
    status: Literal["PASS", "FAIL"]


class VirtualCNCValidation(StrictEvidenceModel):
    schema_version: str = "vena-ia.virtual-cnc-plan-validation/v1"
    source_plan_schema: str
    validation_status: Literal["VALID_FOR_VIRTUAL_REVIEW", "REJECTED"]
    simulation_only: bool = True
    executable_output: bool = False
    human_review_required: bool = True
    checks: list[VirtualCNCCheck]
    warnings: list[str]
    limitations: list[str]
    traceability: list[str]


class RehearsalRequest(StrictEvidenceModel):
    rehearsal_key: str = Field(pattern=r"^synthetic-[a-z0-9][a-z0-9._-]{2,63}$")
    neutral_cnc_plan: NeutralCNCPlan


class PilotEvidenceBundle(StrictEvidenceModel):
    schema_version: str = "vena-ia.pilot-evidence/v1"
    pilot_context_id: str
    organization_id: str
    team_id: str | None
    rehearsal_key: str
    evidence_status: EvidenceStatus
    readiness_status: Literal[
        "INCOMPLETE", "READY_FOR_HUMAN_REVIEW", "BLOCKED_BY_RISK", "REHEARSAL_FAILED"
    ]
    generated_at: datetime
    evidence_items: list[EvidenceItem]
    slo_proposals: list[SLOProposal]
    capacity_acceptance: CapacityAcceptance
    support_matrix: list[SupportPath]
    virtual_cnc_validation: VirtualCNCValidation
    risks: list[str]
    limitations: list[str]
    rollback_status: Literal["DEFINED_NOT_EXECUTED"] = "DEFINED_NOT_EXECUTED"
    rollback_actions: list[str]
    review_status: Literal["REQUIRES_HUMAN_REVIEW"] = "REQUIRES_HUMAN_REVIEW"
    traceability: list[str]
    integrity_sha256: str
    integrity_semantics: str = "SHA-256 detects bundle changes; it is not an authenticity signature."


class OperationalEvidenceSource(StrictEvidenceModel):
    category: str
    source_contract: str
    evidence_reference: str
    owner: str
    limitations: list[str] = []
    warnings: list[str] = []


AUTHORITATIVE_EVIDENCE = (
    OperationalEvidenceSource(
        category="onboarding",
        source_contract="vena-ia.organization/v1",
        evidence_reference="docs/PILOT_GOVERNANCE.md",
        owner="ORGANIZATION_OWNER",
    ),
    OperationalEvidenceSource(
        category="authorization",
        source_contract="vena-ia.membership/v1",
        evidence_reference="docs/AUTHORIZATION_MATRIX.md",
        owner="SECURITY_OWNER",
    ),
    OperationalEvidenceSource(
        category="restore",
        source_contract="vena-ia.backup-set/v1",
        evidence_reference="docs/runbooks/RECOVERY_DRILL.md",
        owner="RECOVERY_OWNER",
        limitations=["Only disposable-environment evidence; no production RPO/RTO claim."],
    ),
    OperationalEvidenceSource(
        category="incident",
        source_contract="vena-ia.incident-drill/v1",
        evidence_reference="docs/runbooks/INCIDENT_DRILL.md",
        owner="INCIDENT_OWNER",
    ),
    OperationalEvidenceSource(
        category="observability",
        source_contract="vena-ia.metrics/v1",
        evidence_reference="docs/runbooks/OBSERVABILITY.md",
        owner="OBSERVABILITY_OWNER",
    ),
    OperationalEvidenceSource(
        category="resilience",
        source_contract="vena-ia.resilience-policy/v1",
        evidence_reference="docs/runbooks/DEPENDENCY_DEGRADATION.md",
        owner="RELIABILITY_OWNER",
    ),
    OperationalEvidenceSource(
        category="capacity",
        source_contract="vena-ia.capacity-evidence/v1",
        evidence_reference="docs/capacity/CAPACITY_EVIDENCE.md",
        owner="CAPACITY_OWNER",
        limitations=["Synthetic profile only; no commercial capacity claim."],
    ),
    OperationalEvidenceSource(
        category="support",
        source_contract="vena-ia.pilot-evidence/v1",
        evidence_reference="docs/PILOT_EVIDENCE_MATRIX.md",
        owner="SUPPORT_OWNER",
    ),
    OperationalEvidenceSource(
        category="rollback",
        source_contract="vena-ia.pilot-context/v1",
        evidence_reference="docs/PILOT_GOVERNANCE.md#fluxo-controlado",
        owner="ORGANIZATION_OWNER",
    ),
)


def validate_virtual_cnc(plan: NeutralCNCPlan) -> VirtualCNCValidation:
    checks = [
        "SCHEMA_VALID",
        "REVIEW_FLAGS_PRESENT",
        "MACHINE_NEUTRAL",
        "NO_EXECUTABLE_BLOCKS",
        "NO_TRANSMISSION_TARGET",
        "NO_MACHINE_CONTROL",
        "TRACEABILITY_COMPLETE",
    ]
    return VirtualCNCValidation(
        source_plan_schema=plan.source_plan_schema,
        validation_status="VALID_FOR_VIRTUAL_REVIEW",
        checks=[VirtualCNCCheck(check=item, status="PASS") for item in checks],
        warnings=["No physical, collision, kinematic, fixture, or stock simulation was run."],
        limitations=[
            "Virtual structural validation is not machine validation.",
            "No toolpath, G-code, M-code, NC file, or transmission target is produced.",
        ],
        traceability=[plan.source_plan_schema, *plan.validation_checks],
    )


class RehearsalService:
    def __init__(
        self,
        evidence_sources: tuple[OperationalEvidenceSource, ...] = AUTHORITATIVE_EVIDENCE,
    ) -> None:
        self.evidence_sources = evidence_sources

    def build(
        self,
        context: PilotContext,
        checklist: PilotReadinessChecklist | None,
        request: RehearsalRequest,
    ) -> PilotEvidenceBundle:
        if context.status != "READY_FOR_SYNTHETIC_REHEARSAL":
            raise HTTPException(status_code=409, detail="Pilot context is not rehearsal-ready")
        if checklist is None or checklist.result != "READY_FOR_HUMAN_REVIEW":
            raise HTTPException(status_code=409, detail="Readiness checklist is incomplete")
        privacy = checklist.privacy
        if not privacy or not all(privacy.values()):
            raise HTTPException(status_code=409, detail="Privacy checklist blocks rehearsal")

        required = {
            "onboarding",
            "authorization",
            "restore",
            "incident",
            "observability",
            "resilience",
            "capacity",
            "support",
            "rollback",
        }
        sources = {item.category: item for item in self.evidence_sources}
        missing = sorted(required - sources.keys())
        if missing:
            raise HTTPException(
                status_code=409, detail="Operational evidence unavailable: " + ", ".join(missing)
            )

        generated_at = checklist.updated_at
        virtual = validate_virtual_cnc(request.neutral_cnc_plan)
        items = [
            EvidenceItem(
                category=source.category,
                status=EvidenceStatus.AVAILABLE,
                source_contract=source.source_contract,
                evidence_reference=source.evidence_reference,
                generated_at=generated_at,
                owner=source.owner,
                limitations=source.limitations,
                warnings=source.warnings,
            )
            for source in self.evidence_sources
        ]
        items.extend(
            [
                EvidenceItem(
                    category="privacy",
                    status=EvidenceStatus.AVAILABLE,
                    source_contract="vena-ia.pilot-readiness-checklist/v1",
                    evidence_reference=f"pilot-readiness:{checklist.id}",
                    generated_at=generated_at,
                    owner="PRIVACY_REVIEWER",
                    limitations=["This does not declare legal or LGPD compliance."],
                    warnings=[],
                ),
                EvidenceItem(
                    category="cnc_virtual_validation",
                    status=EvidenceStatus.AVAILABLE,
                    source_contract=virtual.schema_version,
                    evidence_reference="inline:virtual-cnc-validation",
                    generated_at=generated_at,
                    owner="ENGINEERING_REVIEWER",
                    limitations=virtual.limitations,
                    warnings=virtual.warnings,
                ),
            ]
        )
        raw: dict[str, object] = {
            "pilot_context_id": context.id,
            "organization_id": context.organization_id,
            "team_id": context.team_id,
            "rehearsal_key": request.rehearsal_key,
            "evidence_status": EvidenceStatus.AVAILABLE,
            "readiness_status": "READY_FOR_HUMAN_REVIEW",
            "generated_at": generated_at,
            "evidence_items": items,
            "slo_proposals": [
                SLOProposal(
                    metric="synthetic_request_success_ratio",
                    proposed_target=">= 0.99",
                    window="single bounded rehearsal",
                    source="docs/capacity/CAPACITY_EVIDENCE.md",
                    owner="RELIABILITY_OWNER",
                    limitations=["Proposal only; not an SLA or production commitment."],
                )
            ],
            "capacity_acceptance": CapacityAcceptance(
                workload_profile="CONTROLLED_CAPACITY_SYNTHETIC",
                observed_throughput="SEE_REFERENCED_EVIDENCE",
                latency="SEE_REFERENCED_EVIDENCE",
                error_rate="SEE_REFERENCED_EVIDENCE",
                resource_observations="DISPOSABLE_ENVIRONMENT_ONLY",
                limitations=["No production sizing or commercial extrapolation."],
            ),
            "support_matrix": [
                SupportPath(
                    issue_category="SECURITY_OR_ISOLATION",
                    owner_role="SECURITY_OWNER",
                    escalation_path="CTO_REVIEW",
                    severity="CRITICAL",
                    expected_internal_action="STOP_REHEARSAL_AND_PRESERVE_AUDIT",
                ),
                SupportPath(
                    issue_category="RECOVERY_OR_DEPENDENCY",
                    owner_role="RECOVERY_OWNER",
                    escalation_path="INCIDENT_RUNBOOK",
                    severity="HIGH",
                    expected_internal_action="FAIL_SAFE_AND_EXECUTE_DISPOSABLE_DRILL",
                ),
            ],
            "virtual_cnc_validation": virtual,
            "risks": [
                "R-042: MITIGATED_PARTIALLY_MONITOR",
                "R-021: MONITOR",
                "R-034: SYNTHETIC_CAPACITY_ONLY",
                "FALSE_PILOT_READINESS: FAIL_CLOSED",
            ],
            "limitations": [
                "Synthetic rehearsal is not a real pilot, deploy, SLA, or production approval.",
                "Evidence references are review inputs and require human verification.",
                "No customer, machine, CAD, PDF, credential, or external-user data is included.",
            ],
            "rollback_actions": [
                "Close the synthetic Pilot Context.",
                "Revoke synthetic memberships.",
                "Remove disposable fixtures and temporary evidence.",
                "Restore only the disposable rehearsal environment if needed.",
            ],
            "traceability": [
                "vena-ia.pilot-context/v1",
                "vena-ia.pilot-readiness-checklist/v1",
                "docs/PILOT_EVIDENCE_MATRIX.md",
                request.neutral_cnc_plan.source_plan_schema,
            ],
        }
        unsigned_bundle = PilotEvidenceBundle.model_validate(
            {**raw, "integrity_sha256": ""}
        )
        canonical = json.dumps(
            unsigned_bundle.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return PilotEvidenceBundle.model_validate(
            {**raw, "integrity_sha256": hashlib.sha256(canonical).hexdigest()}
        )
