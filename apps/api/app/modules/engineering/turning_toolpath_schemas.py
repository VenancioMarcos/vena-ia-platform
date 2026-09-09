"""Immutable synthetic point-motion contracts. Never physical toolpaths."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


RadialPoint = tuple[Annotated[float, Field(ge=0)], float]
FeedRateType = Literal["MM_PER_REVOLUTION", "MM_PER_MINUTE"]


class _SyntheticContract(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, allow_inf_nan=False,
                              revalidate_instances="always")


class TurningMotionType(StrEnum):
    RAPID = "RAPID"
    CUTTING = "CUTTING"
    RETRACT = "RETRACT"


class TurningToolpathMove(_SyntheticContract):
    start_point: RadialPoint
    end_point: RadialPoint
    motion_type: TurningMotionType
    feed_rate_type: FeedRateType

    @model_validator(mode="after")
    def validate_segment(self) -> TurningToolpathMove:
        if self.start_point == self.end_point:
            raise ValueError("zero-length synthetic moves are not allowed")
        return self


class TurningOperationPlan(_SyntheticContract):
    operation_id: str = Field(min_length=1, max_length=255)
    operation_type: Literal["FACING", "ROUGH_TURNING"]
    passes_count: int = Field(ge=0, le=1000)
    moves: tuple[TurningToolpathMove, ...] = Field(max_length=10_000)

    @model_validator(mode="after")
    def validate_sequence(self) -> TurningOperationPlan:
        cuts = sum(move.motion_type == TurningMotionType.CUTTING for move in self.moves)
        if cuts != self.passes_count:
            raise ValueError("passes_count must equal the number of cutting segments")
        if any(a.end_point != b.start_point for a, b in zip(self.moves, self.moves[1:])):
            raise ValueError("synthetic moves must be continuous")
        return self


class TurningToolpathPlan(_SyntheticContract):
    profile_id: str = Field(min_length=1, max_length=255)
    operations: tuple[TurningOperationPlan, ...] = Field(max_length=2)
    total_cutting_length_mm: float = Field(ge=0)
    is_collision_free: Literal[False] = False
    collision_status: Literal["NOT_VALIDATED"] = "NOT_VALIDATED"
    executable_output: Literal[False] = False
    physical_use_authorized: Literal[False] = False

    @model_validator(mode="after")
    def validate_plan(self) -> TurningToolpathPlan:
        moves = [move for operation in self.operations for move in operation.moves]
        if len(moves) > 10_000:
            raise ValueError("synthetic move limit exceeded")
        if any(a.end_point != b.start_point for a, b in zip(moves, moves[1:])):
            raise ValueError("operations must share a continuous transition")
        length = math.fsum(math.dist(move.start_point, move.end_point) for move in moves
                           if move.motion_type == TurningMotionType.CUTTING)
        if not math.isfinite(length) or not math.isclose(
            length, self.total_cutting_length_mm, abs_tol=1e-9, rel_tol=1e-12,
        ):
            raise ValueError("total cutting length must match synthetic segments")
        return self


class SyntheticTurningParameters(_SyntheticContract):
    axial_depth_mm: float = Field(gt=0)
    radial_depth_mm: float = Field(gt=0)
    axial_allowance_mm: float = Field(ge=0)
    radial_allowance_mm: float = Field(ge=0)
    clearance_mm: float = Field(gt=0)
    feed_rate_type: FeedRateType
