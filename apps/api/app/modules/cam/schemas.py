from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.cam.enums import CompensationType, ToolOrientation, TurningOperationType


class _CamContract(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        revalidate_instances="always",
        str_strip_whitespace=True,
    )


class RzPoint(_CamContract):
    r_mm: float = Field(ge=0)
    z_mm: float


class TurningBoundingBox(_CamContract):
    max_radius_mm: float = Field(gt=0)
    min_z_mm: float
    max_z_mm: float
    total_z_length_mm: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_extents(self) -> TurningBoundingBox:
        if self.max_z_mm <= self.min_z_mm:
            raise ValueError("bounding box must have a positive Z extent")
        expected = self.max_z_mm - self.min_z_mm
        if not math.isclose(self.total_z_length_mm, expected, abs_tol=1e-9, rel_tol=1e-12):
            raise ValueError("total_z_length_mm must match max_z_mm - min_z_mm")
        return self


class TurningToolParams(_CamContract):
    tip_radius_mm: float = Field(gt=0)
    insert_width_mm: float | None = Field(default=None, gt=0)
    cutting_edge_angle_deg: float = Field(gt=0, lt=180)
    cutting_edge_length_mm: float = Field(gt=0)
    orientation: ToolOrientation
    compensation: CompensationType = CompensationType.NONE


class CuttingParameters(_CamContract):
    vc_m_per_min: float = Field(gt=0)
    feed_mm_per_rev: float = Field(gt=0)
    depth_of_cut_mm: float = Field(gt=0)


class MachiningPass(_CamContract):
    sequence: int = Field(ge=1, le=1_000)
    operation_type: TurningOperationType
    coordinates_rz_mm: tuple[RzPoint, ...] = Field(min_length=2, max_length=10_000)
    estimated_removed_volume_mm3: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_path(self) -> MachiningPass:
        if any(a == b for a, b in zip(self.coordinates_rz_mm, self.coordinates_rz_mm[1:])):
            raise ValueError("consecutive pass coordinates must be distinct")
        return self


class TurningStrategyPlanRequest(_CamContract):
    operation_type: TurningOperationType
    profile_data: tuple[RzPoint, ...] = Field(min_length=2, max_length=10_000)
    bounding_box: TurningBoundingBox
    linear_tolerance_mm: float = Field(gt=0, le=1.0)
    material_reference: str = Field(min_length=1, max_length=255)
    stock_radius_mm: float = Field(gt=0)
    stock_front_z_mm: float
    target_front_z_mm: float
    finish_allowance_mm: float = Field(default=0.0, ge=0, le=5.0)
    tool: TurningToolParams
    cutting_parameters: CuttingParameters
    review_status: Literal["PROFILE_AVAILABLE_REQUIRES_REVIEW"]

    @model_validator(mode="after")
    def validate_stock_envelope(self) -> TurningStrategyPlanRequest:
        if self.stock_radius_mm + self.linear_tolerance_mm < self.bounding_box.max_radius_mm:
            raise ValueError("stock radius must contain the declared profile")
        if self.stock_front_z_mm + self.linear_tolerance_mm < self.target_front_z_mm:
            raise ValueError("stock front Z must not be behind target front Z")
        return self


class TurningStrategyPlanResponse(_CamContract):
    status: Literal["PLANNED_REQUIRES_REVIEW"] = "PLANNED_REQUIRES_REVIEW"
    operation_type: TurningOperationType
    passes: tuple[MachiningPass, ...] = Field(min_length=1, max_length=1_000)
    material_removal_volume_mm3: float = Field(ge=0)
    warnings: tuple[str, ...] = Field(min_length=1, max_length=32)
    executable_output: Literal[False] = False
    physical_use_authorized: Literal[False] = False
    g9_status: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    emission_status: Literal["CONTROLLER_PROFILE_UNRESOLVED"] = "CONTROLLER_PROFILE_UNRESOLVED"

    @model_validator(mode="after")
    def validate_volume(self) -> TurningStrategyPlanResponse:
        total = math.fsum(item.estimated_removed_volume_mm3 for item in self.passes)
        if not math.isclose(
            self.material_removal_volume_mm3,
            total,
            abs_tol=1e-8,
            rel_tol=1e-12,
        ):
            raise ValueError("material removal volume must match the pass estimates")
        return self
