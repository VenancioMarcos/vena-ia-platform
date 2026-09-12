"""Synthetic point-only pass decomposition; no tool, collision or NC authority."""

from __future__ import annotations

import hashlib
import json
import math

from app.modules.engineering.turning_schemas import TurningProfile2D, TurningStockCylinder
from app.modules.engineering.turning_toolpath_schemas import (
    RadialPoint,
    SyntheticTurningParameters,
    TurningMotionType,
    TurningOperationPlan,
    TurningToolpathMove,
    TurningToolpathPlan,
)


class SyntheticTurningPlanningError(ValueError):
    pass


def _levels(start: float, target: float, depth: float) -> tuple[float, ...]:
    count = (start - target) / depth
    if not math.isfinite(count) or count > 1000:
        raise SyntheticTurningPlanningError("PASS_LIMIT_EXCEEDED")
    if count <= 0:
        return ()
    # Compute from the index, avoiding accumulated subtraction and overshoot.
    levels: list[float] = []
    previous = start
    for index in range(1, math.ceil(count) + 1):
        level = max(target, start - index * depth)
        if level >= previous:
            raise SyntheticTurningPlanningError("DEPTH_BELOW_NUMERIC_RESOLUTION")
        levels.append(level)
        if level == target:
            break  # Floating-point ceil must not repeat a completed boundary.
        previous = level
    return tuple(levels)


def _regions(profile: TurningProfile2D) -> tuple[tuple[float, float, float], ...]:
    points = profile.points
    if (profile.is_closed or len(points) < 4 or points[0].radius_mm != 0
            or points[-1].radius_mm != 0 or points[0].z_mm != 0
            or points[1].z_mm != 0 or points[-2].z_mm != points[-1].z_mm):
        raise SyntheticTurningPlanningError("EXTERNAL_CYLINDRICAL_PROFILE_REQUIRED")
    outer = points[1:-1]
    regions: list[tuple[float, float, float]] = []
    for a, b in zip(outer, outer[1:]):
        if a.radius_mm <= 0 or b.radius_mm <= 0 or b.z_mm > a.z_mm:
            raise SyntheticTurningPlanningError("INVALID_EXTERNAL_PROFILE")
        if b.radius_mm < a.radius_mm:
            raise SyntheticTurningPlanningError("UNDERCUT_UNSUPPORTED")
        if a.z_mm == b.z_mm:
            continue
        if a.radius_mm != b.radius_mm:
            raise SyntheticTurningPlanningError("NON_CYLINDRICAL_PROFILE")
        regions.append((a.radius_mm, a.z_mm, b.z_mm))
    if not regions or regions[0][1] != 0 or regions[-1][2] != points[-1].z_mm:
        raise SyntheticTurningPlanningError("INVALID_EXTERNAL_PROFILE")
    if any(a[2] != b[1] for a, b in zip(regions, regions[1:])):
        raise SyntheticTurningPlanningError("DISCONTINUOUS_PROFILE")
    return tuple(regions)


def _validate(
    profile: TurningProfile2D, stock: TurningStockCylinder, parameters: SyntheticTurningParameters,
) -> tuple[tuple[float, float, float], ...]:
    # Revalidate at the function boundary, including potentially constructed models.
    profile = TurningProfile2D.model_validate(profile.model_dump())
    stock = TurningStockCylinder.model_validate(stock.model_dump())
    parameters = SyntheticTurningParameters.model_validate(parameters.model_dump())
    regions = _regions(profile)
    if (stock.diameter_mm / 2 < max(r[0] for r in regions) + parameters.radial_allowance_mm
            or stock.face_allowance_mm < parameters.axial_allowance_mm
            or stock.face_allowance_mm - stock.length_mm > regions[-1][2]):
        raise SyntheticTurningPlanningError("STOCK_DOES_NOT_CONTAIN_FINISHED_ENVELOPE")
    # A shoulder allowance must not consume the whole preceding region.
    if any(front - rear <= parameters.axial_allowance_mm for _, front, rear in regions[:-1]):
        raise SyntheticTurningPlanningError("AXIAL_ALLOWANCE_EXCEEDS_REGION")
    safe = _safe_point(stock, parameters)
    if not all(math.isfinite(x) for x in safe):
        raise SyntheticTurningPlanningError("NUMERIC_RANGE_EXCEEDED")
    return regions


def _safe_point(stock: TurningStockCylinder, parameters: SyntheticTurningParameters) -> RadialPoint:
    # A geometric reference location only, not a machine-safe position.
    return (stock.diameter_mm / 2 + parameters.clearance_mm,
            stock.face_allowance_mm + parameters.clearance_mm)


def _move(
    start: RadialPoint, end: RadialPoint, kind: TurningMotionType,
    parameters: SyntheticTurningParameters,
) -> TurningToolpathMove:
    return TurningToolpathMove(start_point=start, end_point=end, motion_type=kind,
                               feed_rate_type=parameters.feed_rate_type)


def plan_facing_passes(
    profile: TurningProfile2D, stock: TurningStockCylinder, parameters: SyntheticTurningParameters,
) -> TurningOperationPlan:
    _validate(profile, stock, parameters)
    levels = _levels(stock.face_allowance_mm, parameters.axial_allowance_mm,
                     parameters.axial_depth_mm)
    safe = _safe_point(stock, parameters)
    moves: list[TurningToolpathMove] = []
    for z in levels:
        outside, center, relieved = (safe[0], z), (0.0, z), (0.0, safe[1])
        moves.extend((
            _move(safe, outside, TurningMotionType.RAPID, parameters),
            _move(outside, center, TurningMotionType.CUTTING, parameters),
            _move(center, relieved, TurningMotionType.RETRACT, parameters),
            _move(relieved, safe, TurningMotionType.RAPID, parameters),
        ))
    return TurningOperationPlan(operation_id="synthetic-facing", operation_type="FACING",
                                passes_count=len(levels), moves=tuple(moves))


def plan_longitudinal_roughing(
    profile: TurningProfile2D, stock: TurningStockCylinder, parameters: SyntheticTurningParameters,
) -> TurningOperationPlan:
    regions = _validate(profile, stock, parameters)
    # Reach every diameter's finish boundary; a single global grid can leave
    # excessive material on a larger rear step when ap does not divide its stock.
    levels_list: list[float] = []
    previous = stock.diameter_mm / 2
    targets = sorted({region[0] + parameters.radial_allowance_mm for region in regions},
                     reverse=True)
    for target in targets:
        levels_list.extend(_levels(previous, target, parameters.radial_depth_mm))
        if len(levels_list) > 1000:
            raise SyntheticTurningPlanningError("PASS_LIMIT_EXCEEDED")
        previous = target
    levels = tuple(levels_list)
    safe = _safe_point(stock, parameters)
    moves: list[TurningToolpathMove] = []
    for radius in levels:
        rear = regions[-1][2]
        for target_radius, front, _ in regions:
            if radius < target_radius + parameters.radial_allowance_mm:
                rear = front + parameters.axial_allowance_mm
                break
        start, end, outside = (radius, safe[1]), (radius, rear), (safe[0], rear)
        moves.extend((
            _move(safe, start, TurningMotionType.RAPID, parameters),
            _move(start, end, TurningMotionType.CUTTING, parameters),
            _move(end, outside, TurningMotionType.RETRACT, parameters),
            _move(outside, safe, TurningMotionType.RAPID, parameters),
        ))
    return TurningOperationPlan(operation_id="synthetic-longitudinal",
                                operation_type="ROUGH_TURNING", passes_count=len(levels),
                                moves=tuple(moves))


def generate_turning_roughing_plan(
    profile: TurningProfile2D, stock: TurningStockCylinder, parameters: SyntheticTurningParameters,
) -> TurningToolpathPlan:
    _validate(profile, stock, parameters)
    operations = (plan_facing_passes(profile, stock, parameters),
                  plan_longitudinal_roughing(profile, stock, parameters))
    length = math.fsum(math.dist(move.start_point, move.end_point)
                       for operation in operations for move in operation.moves
                       if move.motion_type == TurningMotionType.CUTTING)
    canonical = json.dumps(profile.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    profile_id = "synthetic-profile:sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    return TurningToolpathPlan(profile_id=profile_id, operations=operations,
                               total_cutting_length_mm=length)
