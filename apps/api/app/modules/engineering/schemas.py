from datetime import datetime
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
