"""Continuous checks of declared synthetic boundaries, without physical authority."""

from __future__ import annotations

from fractions import Fraction
from typing import Annotated

from pydantic import Field, TypeAdapter

from app.modules.engineering.turning_toolpath_schemas import (
    TurningBoundaryStatus, TurningChuckFixture, TurningStaticExclusionZone,
    TurningToolEnvelope2D, TurningToolpathPlan, TurningVerificationReport,
)


_Zones = Annotated[tuple[TurningStaticExclusionZone, ...], Field(max_length=128)]
_ZONE_ADAPTER = TypeAdapter(_Zones)
_Point = tuple[Fraction, Fraction]
_Rectangle = tuple[Fraction, Fraction, Fraction, Fraction]


def _intersects(start: _Point, end: _Point, rect: _Rectangle) -> bool:
    """Closed slab intersection over t in [0,1], exact for declared binary floats."""
    enter, leave = Fraction(0), Fraction(1)
    for a, b, low, high in (
        (start[0], end[0], rect[0], rect[1]),
        (start[1], end[1], rect[2], rect[3]),
    ):
        delta = b - a
        if delta == 0:
            if not low <= a <= high:
                return False
            continue
        first, last = sorted(((low - a) / delta, (high - a) / delta))
        enter, leave = max(enter, first), min(leave, last)
        if enter > leave:
            return False
    return True


def verify_toolpath_boundaries(
    plan: TurningToolpathPlan,
    fixture: TurningChuckFixture,
    tool: TurningToolEnvelope2D,
    exclusion_zones: tuple[TurningStaticExclusionZone, ...],
) -> TurningVerificationReport:
    """Reject invalid input; report only the declared static mathematical scope.

    All movement types use closed boundaries. Indices are global, zero-based.
    A negative ideal radius is rejected by revalidation (including forged models),
    so CENTERLINE_VIOLATION is reserved and unreachable for valid input. Precedence
    for valid moves is chuck before declared zones; every violating index is kept.
    Exact rationals avoid overflow and boundary-rounding errors in this checker;
    they do not remove input uncertainty or provide physical collision evidence.
    """
    plan = TurningToolpathPlan.model_validate(plan)
    fixture = TurningChuckFixture.model_validate(fixture)
    tool = TurningToolEnvelope2D.model_validate(tool)
    zones = _ZONE_ADAPTER.validate_python(exclusion_zones, strict=True)
    if len({zone.zone_id for zone in zones}) != len(zones):
        raise ValueError("declared zone ids must be unique")
    moves = tuple(move for operation in plan.operations for move in operation.moves)
    if len(moves) * max(1, len(zones)) > 200_000:
        raise ValueError("synthetic boundary verification budget exceeded")

    # Negative offsets use the reflected local AABB: [zone.min-tool.max, zone.max-tool.min].
    rectangles = tuple((
        Fraction(zone.r_min_mm) - Fraction(tool.shank_r_max_mm),
        Fraction(zone.r_max_mm) - Fraction(tool.shank_r_min_mm),
        Fraction(zone.z_min_mm) - Fraction(tool.shank_z_max_mm),
        Fraction(zone.z_max_mm) - Fraction(tool.shank_z_min_mm),
    ) for zone in zones)
    chuck_limit = Fraction(fixture.z_chuck_plane_mm) + Fraction(fixture.safety_clearance_axial_mm)
    # Check both ideal point and envelope, including a shank entirely ahead of the point.
    chuck_offset = min(Fraction(0), Fraction(tool.shank_z_min_mm))
    violating: list[int] = []
    chuck_collision = False
    for index, move in enumerate(moves):
        start = (Fraction(move.start_point[0]), Fraction(move.start_point[1]))
        end = (Fraction(move.end_point[0]), Fraction(move.end_point[1]))
        touches_chuck = min(start[1], end[1]) + chuck_offset <= chuck_limit
        touches_zone = any(_intersects(start, end, rect) for rect in rectangles)
        if touches_chuck or touches_zone:
            violating.append(index)
        chuck_collision |= touches_chuck

    status: TurningBoundaryStatus
    if not moves:
        status = "NOT_EVALUATED"
    elif chuck_collision:
        status = "CHUCK_COLLISION_DETECTED"
    elif violating:
        status = "DECLARED_ZONE_INTERFERENCE"
    else:
        status = "PASS"
    return TurningVerificationReport(
        boundary_status=status, declared_boundaries_passed=status == "PASS",
        violating_moves=tuple(violating),
    )
