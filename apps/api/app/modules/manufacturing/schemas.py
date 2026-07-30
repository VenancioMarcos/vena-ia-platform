from enum import StrEnum

from pydantic import BaseModel, Field


class MaterialFamily(StrEnum):
    ALUMINUM = "ALUMINUM"
    CARBON_STEEL = "CARBON_STEEL"
    STAINLESS_STEEL = "STAINLESS_STEEL"


class MillingInput(BaseModel):
    material: MaterialFamily
    tool_diameter_mm: float = Field(gt=0, le=200)
    tool_teeth: int = Field(ge=1, le=20)
    cutting_length_mm: float = Field(gt=0, le=1_000_000)
    machine_max_rpm: float = Field(gt=0, le=100_000)
    machine_max_feed_mm_min: float = Field(gt=0, le=100_000)


class MillingRecommendation(BaseModel):
    operation: str
    material: MaterialFamily
    cutting_speed_m_min: float
    feed_per_tooth_mm: float
    spindle_rpm: float
    feed_mm_min: float
    estimated_cutting_time_min: float
    limiting_factors: list[str]
    status: str
    calculation_basis: list[str]
