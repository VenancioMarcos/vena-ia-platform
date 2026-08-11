from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.engineering.schemas import EngineeringRecommendationReference


Point3D = tuple[float, float, float]


class StockDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal[
        "PROVIDED",
        "DERIVED_FROM_AUTHORIZED_CONFIGURATION",
        "MISSING",
        "AMBIGUOUS",
        "INVALID",
    ]
    minimum: Point3D | None = None
    maximum: Point3D | None = None
    unit: Literal["mm"] = "mm"
    source_ref: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_bounds(self) -> "StockDefinition":
        if self.status in {"PROVIDED", "DERIVED_FROM_AUTHORIZED_CONFIGURATION"}:
            if self.minimum is None or self.maximum is None or not self.source_ref:
                raise ValueError("Available stock requires bounds and source_ref")
        return self


class ManufacturingPlanningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(min_length=1, max_length=255)
    stock: StockDefinition | None = None
    manufacturing_intent: Literal["milling", "drilling"] | None = None
    material_id: str | None = Field(default=None, min_length=1, max_length=255)
    machine_id: str | None = Field(default=None, min_length=1, max_length=255)
    tool_id: str | None = Field(default=None, min_length=1, max_length=255)
    fixture: str | None = Field(default=None, min_length=1, max_length=500)
    datum_wcs_input: str | None = Field(default=None, min_length=1, max_length=500)
    drawing_tolerance: str | None = Field(default=None, min_length=1, max_length=255)
    surface_finish: str | None = Field(default=None, min_length=1, max_length=255)
    material_condition: str | None = Field(default=None, min_length=1, max_length=255)


class MissingManufacturingInput(BaseModel):
    field: str
    reason: str
    blocking_gate: str
    expected_type_unit: str
    evidence_missing: list[str]


class FinalGeometryReference(BaseModel):
    source_geometry_hash: str
    topology_evidence_schema: str
    topology_evidence_hash: str
    normalized_unit: str
    bounds: tuple[Point3D, Point3D]
    topology_valid: bool


class StockEvidence(BaseModel):
    status: str
    minimum: Point3D | None
    maximum: Point3D | None
    unit: str | None
    source_ref: str | None
    contains_final_geometry: bool | None
    volume: float | None
    limitations: list[str]


class ManufacturingRegion(BaseModel):
    region_id: str
    region_type: str
    status: str
    bounds: tuple[Point3D, Point3D] | None
    volume: float | None
    topology_refs: list[str]
    evidence: list[str]
    limitations: list[str]


class AccessibilityCandidate(BaseModel):
    candidate_id: str
    approach_direction: Point3D
    accessible_surface_refs: list[str]
    blocked_surface_refs: list[str]
    status: str
    evidence: list[str]
    limitations: list[str]


class DatumCandidate(BaseModel):
    candidate_id: str
    surface_ref: str
    origin_candidate: Point3D
    normal: Point3D
    area: float
    status: str = "REQUIRES_REVIEW"


class WCSCandidate(BaseModel):
    candidate_id: str
    datum_candidate_id: str
    origin: Point3D
    z_direction: Point3D
    status: str = "REQUIRES_REVIEW"


class SetupCandidate(BaseModel):
    candidate_id: str
    orientation: Point3D
    accessibility_candidate_id: str
    fixture_status: str
    status: str
    evidence: list[str]
    limitations: list[str]


class ProcessOperationCandidate(BaseModel):
    candidate_id: str
    operation_class: str
    requested_intent: str
    setup_candidate_id: str | None
    target_region_refs: list[str]
    resource_requirements: list[str]
    parameters: dict[str, object]
    missing_parameters: list[str]
    dependencies: list[str]
    status: str
    evidence: list[str]
    executable_output: bool = False


class PlanningVerificationEvidence(BaseModel):
    schema_version: str = "vena-ia.planning-verification-evidence/v1"
    status: str
    coherent: bool
    logical_coverage: str
    missing_input_count: int
    resource_compatibility: str
    precedence_valid: bool
    setup_feasibility: str
    deterministic_replay_hash: str
    checks: list[str]
    limitations: list[str]
    physical_validation: bool = False


class ManufacturingGeometryModel(BaseModel):
    schema_version: str = "vena-ia.manufacturing-geometry-model/v1"
    planning_schema_version: str = "vena-ia.verified-process-plan/v1"
    status: str
    final_geometry: FinalGeometryReference
    stock: StockEvidence
    removal_regions: list[ManufacturingRegion]
    protected_regions: list[ManufacturingRegion]
    inaccessible_regions: list[ManufacturingRegion]
    unknown_regions: list[ManufacturingRegion]
    accessibility_candidates: list[AccessibilityCandidate]
    datum_candidates: list[DatumCandidate]
    wcs_candidates: list[WCSCandidate]
    setup_candidates: list[SetupCandidate]
    operation_candidates: list[ProcessOperationCandidate]
    precedence_rules: list[str]
    missing_inputs: list[MissingManufacturingInput]
    ambiguities: list[str]
    geometric_constraints: list[str]
    assumptions: list[str]
    confidence_evidence: list[str]
    provenance: list[str]
    limitations: list[str]
    recommendation: EngineeringRecommendationReference | None
    verification: PlanningVerificationEvidence
    review_state: str = "REQUIRES_HUMAN_REVIEW"
    executable_output: bool = False
