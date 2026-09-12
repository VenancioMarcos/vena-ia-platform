from __future__ import annotations

import math
from dataclasses import dataclass

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import (
    MachiningPass,
    RzPoint,
    TurningStrategyPlanRequest,
    TurningStrategyPlanResponse,
)


MAX_PASSES = 1_000
REVIEW_WARNINGS = (
    "ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW",
    "NO_REAL_TOOL_FIXTURE_OR_COLLISION_VALIDATION",
)


class TurningStrategyValidationError(ValueError):
    """Stable fail-closed reason for an invalid or unsupported CAM input."""


@dataclass(frozen=True)
class _AxialSpan:
    radius_mm: float
    front_z_mm: float
    rear_z_mm: float

    @property
    def length_mm(self) -> float:
        return self.front_z_mm - self.rear_z_mm


def _validate_profile(request: TurningStrategyPlanRequest) -> None:
    bounds = request.bounding_box
    tolerance = request.linear_tolerance_mm
    points = request.profile_data
    for point in points:
        if (
            point.r_mm < 0
            or point.r_mm > bounds.max_radius_mm + tolerance
            or point.z_mm < bounds.min_z_mm - tolerance
            or point.z_mm > bounds.max_z_mm + tolerance
        ):
            raise TurningStrategyValidationError("PROFILE_OUTSIDE_DECLARED_BOUNDING_BOX")

    if not math.isclose(
        max(point.r_mm for point in points),
        bounds.max_radius_mm,
        abs_tol=tolerance,
        rel_tol=0,
    ):
        raise TurningStrategyValidationError("PROFILE_BOUNDING_RADIUS_MISMATCH")
    if not math.isclose(
        min(point.z_mm for point in points), bounds.min_z_mm, abs_tol=tolerance, rel_tol=0
    ) or not math.isclose(
        max(point.z_mm for point in points), bounds.max_z_mm, abs_tol=tolerance, rel_tol=0
    ):
        raise TurningStrategyValidationError("PROFILE_BOUNDING_Z_MISMATCH")


def _levels(start: float, target: float, maximum_depth: float) -> tuple[float, ...]:
    if start <= target:
        raise TurningStrategyValidationError("NO_POSITIVE_MATERIAL_ALLOWANCE")
    count = math.ceil((start - target) / maximum_depth)
    if count > MAX_PASSES:
        raise TurningStrategyValidationError("PASS_LIMIT_EXCEEDED")
    return tuple(max(target, start - maximum_depth * index) for index in range(1, count + 1))


def _plan_facing(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    tolerance = request.linear_tolerance_mm
    if request.stock_front_z_mm - request.target_front_z_mm <= tolerance:
        raise TurningStrategyValidationError("NO_POSITIVE_FACE_ALLOWANCE")

    levels = _levels(
        request.stock_front_z_mm,
        request.target_front_z_mm,
        request.cutting_parameters.depth_of_cut_mm,
    )
    previous_z = request.stock_front_z_mm
    passes: list[MachiningPass] = []
    for sequence, z_level in enumerate(levels, start=1):
        volume = math.pi * request.stock_radius_mm**2 * (previous_z - z_level)
        passes.append(
            MachiningPass(
                sequence=sequence,
                operation_type=TurningOperationType.FACING,
                coordinates_rz_mm=(
                    RzPoint(r_mm=request.stock_radius_mm, z_mm=z_level),
                    RzPoint(r_mm=0.0, z_mm=z_level),
                ),
                estimated_removed_volume_mm3=volume,
            )
        )
        previous_z = z_level
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.FACING,
        passes=tuple(passes),
        material_removal_volume_mm3=math.fsum(
            item.estimated_removed_volume_mm3 for item in passes
        ),
        warnings=REVIEW_WARNINGS,
    )


def _profile_spans(request: TurningStrategyPlanRequest) -> tuple[_AxialSpan, ...]:
    tolerance = request.linear_tolerance_mm
    spans = [
        _AxialSpan(
            radius_mm=first.r_mm,
            front_z_mm=max(first.z_mm, second.z_mm),
            rear_z_mm=min(first.z_mm, second.z_mm),
        )
        for first, second in zip(request.profile_data, request.profile_data[1:])
        if first.r_mm > tolerance
        and math.isclose(first.r_mm, second.r_mm, abs_tol=tolerance, rel_tol=0)
        and abs(first.z_mm - second.z_mm) > tolerance
    ]
    spans.sort(key=lambda item: (-item.front_z_mm, -item.rear_z_mm))
    if not spans:
        raise TurningStrategyValidationError("UNSUPPORTED_PROFILE_WITHOUT_AXIAL_SPANS")

    expected_front = request.bounding_box.max_z_mm
    previous_radius = -math.inf
    for span in spans:
        if not math.isclose(span.front_z_mm, expected_front, abs_tol=tolerance, rel_tol=0):
            raise TurningStrategyValidationError("PROFILE_AXIAL_SPANS_DISCONTINUOUS")
        if span.radius_mm + tolerance < previous_radius:
            raise TurningStrategyValidationError("PROFILE_REQUIRES_UNSUPPORTED_REAR_APPROACH")
        previous_radius = span.radius_mm
        expected_front = span.rear_z_mm
    if not math.isclose(
        expected_front, request.bounding_box.min_z_mm, abs_tol=tolerance, rel_tol=0
    ):
        raise TurningStrategyValidationError("PROFILE_AXIAL_SPANS_INCOMPLETE")
    return tuple(spans)


def _roughing_levels(
    stock_radius_mm: float,
    spans: tuple[_AxialSpan, ...],
    maximum_depth_mm: float,
) -> tuple[float, ...]:
    minimum = min(span.radius_mm for span in spans)
    base = _levels(stock_radius_mm, minimum, maximum_depth_mm)
    breakpoints = {span.radius_mm for span in spans if span.radius_mm < stock_radius_mm}
    result = tuple(sorted(set(base).union(breakpoints), reverse=True))
    if len(result) > MAX_PASSES:
        raise TurningStrategyValidationError("PASS_LIMIT_EXCEEDED")
    return result


def _plan_roughing(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    spans = _profile_spans(request)
    levels = _roughing_levels(
        request.stock_radius_mm,
        spans,
        request.cutting_parameters.depth_of_cut_mm,
    )
    current_radii = [request.stock_radius_mm] * len(spans)
    passes: list[MachiningPass] = []
    for radius in levels:
        traversed: list[int] = []
        for index, span in enumerate(spans):
            if radius + request.linear_tolerance_mm < span.radius_mm:
                break
            traversed.append(index)
        if not traversed:
            continue

        removed = 0.0
        for index in traversed:
            previous = current_radii[index]
            if radius < previous:
                removed += math.pi * (previous**2 - radius**2) * spans[index].length_mm
                current_radii[index] = radius
        if removed <= 0:
            continue
        rear_z = spans[traversed[-1]].rear_z_mm
        sequence = len(passes) + 1
        passes.append(
            MachiningPass(
                sequence=sequence,
                operation_type=TurningOperationType.ROUGH_TURNING,
                coordinates_rz_mm=(
                    RzPoint(r_mm=request.stock_radius_mm, z_mm=spans[0].front_z_mm),
                    RzPoint(r_mm=radius, z_mm=spans[0].front_z_mm),
                    RzPoint(r_mm=radius, z_mm=rear_z),
                    RzPoint(r_mm=request.stock_radius_mm, z_mm=rear_z),
                ),
                estimated_removed_volume_mm3=removed,
            )
        )

    if not passes or any(
        current > span.radius_mm + request.linear_tolerance_mm
        for current, span in zip(current_radii, spans)
    ):
        raise TurningStrategyValidationError("ROUGHING_PLAN_INCOMPLETE")
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.ROUGH_TURNING,
        passes=tuple(passes),
        material_removal_volume_mm3=math.fsum(
            item.estimated_removed_volume_mm3 for item in passes
        ),
        warnings=REVIEW_WARNINGS,
    )


def plan_turning_strategy(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    """Build a deterministic review-only 2D plan without machine or NC authority."""
    _validate_profile(request)
    if request.operation_type == TurningOperationType.FACING:
        return _plan_facing(request)
    if request.operation_type == TurningOperationType.ROUGH_TURNING:
        return _plan_roughing(request)
    raise TurningStrategyValidationError("OPERATION_NOT_IMPLEMENTED_IN_FOUNDATION")
