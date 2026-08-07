from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


REVIEW_STATUS = "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"


class CatalogKind(StrEnum):
    MATERIAL = "MATERIAL"
    MACHINE = "MACHINE"
    TOOL = "TOOL"


class CatalogScope(StrEnum):
    SYSTEM_REFERENCE = "SYSTEM_REFERENCE"
    ORGANIZATION_OWNED = "ORGANIZATION_OWNED"
    LEGACY_UNSCOPED = "LEGACY_UNSCOPED"


class CatalogLifecycle(StrEnum):
    ACTIVE = "ACTIVE"
    SYSTEM_READ_ONLY = "SYSTEM_READ_ONLY"


class CatalogRetentionStatus(StrEnum):
    RETAINED_FOR_TRACEABILITY_NO_TEMPORAL_POLICY = (
        "RETAINED_FOR_TRACEABILITY_NO_TEMPORAL_POLICY"
    )
    SYSTEM_MANAGED_NO_TENANT_POLICY = "SYSTEM_MANAGED_NO_TENANT_POLICY"


class CatalogDeletionStatus(StrEnum):
    DELETE_NOT_EXPOSED = "DELETE_NOT_EXPOSED"
    SYSTEM_MUTATION_NOT_EXPOSED = "SYSTEM_MUTATION_NOT_EXPOSED"


class CatalogReconciliationStatus(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SYSTEM_REFERENCE_NOT_RECONCILABLE = "SYSTEM_REFERENCE_NOT_RECONCILABLE"


class CatalogItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: CatalogKind
    code: str = Field(min_length=1, max_length=100, pattern=r"^[A-Z0-9._-]+$")
    name: str = Field(min_length=1, max_length=255)
    data_version: str = Field(min_length=1, max_length=64)
    source: str = Field(min_length=1, max_length=2000)
    properties: dict[str, object]


class CatalogItemRead(CatalogItemCreate):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.engineering-catalog/v1"
    id: str
    scope_type: CatalogScope
    organization_id: str | None
    created_by: str
    created_at: datetime


class CatalogGovernanceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: CatalogKind
    code: str
    data_version: str


class CatalogGovernanceEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "vena-ia.engineering-governance-evidence/v1"
    catalog_reference: CatalogGovernanceReference
    scope_type: CatalogScope
    organization_reference: str | None
    provenance: str
    created_at: datetime
    created_by: str
    lifecycle_status: CatalogLifecycle
    audit_references: list[str]
    retention_status: CatalogRetentionStatus
    deletion_status: CatalogDeletionStatus
    reconciliation_status: CatalogReconciliationStatus
    limitations: list[str]
    warnings: list[str]
    review_status: str = "GOVERNANCE_EVIDENCE_REQUIRES_HUMAN_REVIEW"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    material_id: str
    machine_id: str
    tool_id: str
    operation: str = Field(min_length=1, max_length=100)


class PreliminarySelection(BaseModel):
    schema_version: str = "vena-ia.engineering-selection/v1"
    status: str = REVIEW_STATUS
    operation: str
    material: CatalogItemRead
    machine: CatalogItemRead
    tool: CatalogItemRead
    traceability: list[str]
    limitations: list[str]


class RecommendationRequest(SelectionRequest):
    cutting_length_mm: float | None = Field(default=None, gt=0, le=1_000_000)
    setup_time_min: float | None = Field(default=None, ge=0, le=100_000)
    machine_hour_rate: float | None = Field(default=None, ge=0, le=1_000_000)
    tool_cost_allocation: float | None = Field(default=None, ge=0, le=1_000_000)
    consumable_cost: float | None = Field(default=None, ge=0, le=1_000_000)
    overhead_cost: float | None = Field(default=None, ge=0, le=1_000_000)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class AvailabilityValue(BaseModel):
    status: str
    value: float | None = None
    unit: str | None = None
    reason: str | None = None


class EngineeringRecommendation(BaseModel):
    schema_version: str = "vena-ia.engineering-recommendation/v1"
    status: str = REVIEW_STATUS
    compatibility: str
    operation: str
    material: CatalogItemRead
    machine: CatalogItemRead
    tool: CatalogItemRead
    preliminary_parameters: dict[str, AvailabilityValue]
    formulas: list[str]
    units: dict[str, str]
    assumptions: list[str]
    limitations: list[str]
    traceability: list[str]
    data_versions: dict[str, str]
    rule_version: str
    source: str
    source_version: str
    machining_time_estimate: AvailabilityValue
    setup_time_estimate: AvailabilityValue
    total_estimated_time: AvailabilityValue
    cost_estimate: AvailabilityValue
    cost_components: dict[str, float]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewChecklistItem(BaseModel):
    item: str
    status: str


class EngineeringReviewReport(BaseModel):
    schema_version: str = "vena-ia.engineering-review-report/v1"
    status: str = REVIEW_STATUS
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recommendation_schema_version: str
    operation: str
    material: CatalogItemRead
    machine: CatalogItemRead
    tool: CatalogItemRead
    compatibility: str
    preliminary_parameters: dict[str, AvailabilityValue]
    formulas: list[str]
    units: dict[str, str]
    assumptions: list[str]
    limitations: list[str]
    unavailable_items: list[str]
    time_estimate: AvailabilityValue
    cost_estimate: AvailabilityValue
    traceability: list[str]
    sources: list[str]
    data_versions: dict[str, str]
    rule_version: str
    uncertainty: str
    review_checklist: list[ReviewChecklistItem]
    conclusion: str


class FeaturePlanningRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=255)
    feature_id: str = Field(pattern=r"^feature-[0-9]{4}$")
    material_id: str | None = Field(default=None, min_length=1, max_length=255)
    machine_id: str | None = Field(default=None, min_length=1, max_length=255)
    tool_id: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturing_intent: str | None = Field(default=None, min_length=1, max_length=500)
    drawing_tolerance: str | None = Field(default=None, min_length=1, max_length=255)
    surface_finish: str | None = Field(default=None, min_length=1, max_length=255)
    fixture: str | None = Field(default=None, min_length=1, max_length=500)
    coolant: str | None = Field(default=None, min_length=1, max_length=255)
    material_condition: str | None = Field(default=None, min_length=1, max_length=255)
    setup_time_min: float | None = Field(default=None, ge=0, le=100_000)
    machine_hour_rate: float | None = Field(default=None, ge=0, le=1_000_000)
    tool_cost_allocation: float | None = Field(default=None, ge=0, le=1_000_000)
    consumable_cost: float | None = Field(default=None, ge=0, le=1_000_000)
    overhead_cost: float | None = Field(default=None, ge=0, le=1_000_000)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class FeaturePlanningDimension(BaseModel):
    name: str
    value: float | None
    unit: str
    source: str
    status: str


class FeaturePlanningCandidate(BaseModel):
    candidate_type: str
    operation: str
    status: str
    evidence: list[str]
    executable_output: bool = False


class EngineeringRecommendationReference(BaseModel):
    schema_version: str
    status: str
    compatibility: str
    operation: str
    preliminary_parameters: dict[str, AvailabilityValue]
    limitations: list[str]
    traceability: list[str]
    data_versions: dict[str, str]
    rule_version: str


class FeaturePlanningResponse(BaseModel):
    schema_version: str = "vena-ia.feature-planning/v1"
    status: str
    feature_schema_version: str = "vena-ia.geometry-features/v1"
    engineering_schema_version: str = "vena-ia.engineering-recommendation/v1"
    feature_id: str
    feature_type: str
    feature_dimensions: list[FeaturePlanningDimension]
    planning_rule_version: str
    planning_candidates: list[FeaturePlanningCandidate]
    required_inputs: list[str]
    unavailable_inputs: list[str]
    engineering_recommendation: EngineeringRecommendationReference | None
    planning_context_completeness: str
    geometric_evidence_confidence: str
    assumptions: list[str]
    limitations: list[str]
    traceability: list[str]
    uncertainty: str
    review_status: str = REVIEW_STATUS
