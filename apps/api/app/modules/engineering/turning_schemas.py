"""Preliminary turning input contracts; no planner or controller authority."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Point3D = tuple[float, float, float]


class _TurningContract(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="forbid", allow_inf_nan=False, frozen=True,
        revalidate_instances="always", str_strip_whitespace=True,
    )


class TurningProfilePoint(_TurningContract):
    radius_mm: float = Field(ge=0)
    z_mm: float


class TurningProfile2D(_TurningContract):
    """Declared polyline only; validity does not establish a BRep-derived profile."""

    points: tuple[TurningProfilePoint, ...] = Field(min_length=2, max_length=10_000)
    axis_origin: Point3D
    axis_direction: Point3D
    is_closed: bool

    @model_validator(mode="after")
    def validate_profile(self) -> TurningProfile2D:
        if not math.isclose(math.hypot(*self.axis_direction), 1.0, abs_tol=1e-9, rel_tol=0):
            raise ValueError("axis_direction must be a unit vector")
        if any(a == b for a, b in zip(self.points, self.points[1:])):
            raise ValueError("consecutive profile points must be distinct")
        closed = self.points[0] == self.points[-1]
        if closed != self.is_closed or (closed and len(self.points) < 4):
            raise ValueError("is_closed must match explicit closure with at least four points")
        return self


class TurningStockCylinder(_TurningContract):
    diameter_mm: float = Field(gt=0)
    length_mm: float = Field(gt=0)
    face_allowance_mm: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_allowance(self) -> TurningStockCylinder:
        if self.face_allowance_mm >= self.length_mm:
            raise ValueError("face allowance must leave positive stock length")
        return self


class TurningToolDefinition(_TurningContract):
    tool_id: str = Field(min_length=1, max_length=255)
    insert_radius_mm: float = Field(gt=0)
    hand: Literal["LEFT", "RIGHT", "NEUTRAL"]
    clearance_angle_deg: float = Field(ge=0, lt=90)


class ControllerProfileRequirement(_TurningContract):
    """A declaration to resolve later, never an accepted postprocessor profile."""

    controller_id: str = Field(min_length=1, max_length=255)
    x_mode: Literal["DIAMETER", "RADIUS"]
    feed_mode: Literal["MM_PER_REVOLUTION", "MM_PER_MINUTE"]

    @property
    def emission_status(self) -> Literal["CONTROLLER_PROFILE_UNRESOLVED"]:
        return "CONTROLLER_PROFILE_UNRESOLVED"
