from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


REVIEW_STATUS = "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"


class CatalogKind(StrEnum):
    MATERIAL = "MATERIAL"
    MACHINE = "MACHINE"
    TOOL = "TOOL"


class CatalogItemCreate(BaseModel):
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
    created_by: str
    created_at: datetime


class SelectionRequest(BaseModel):
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
