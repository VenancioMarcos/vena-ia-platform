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
FINISHING_WARNINGS = REVIEW_WARNINGS + (
    "TOOL_CENTER_PATH_INCLUDES_2D_NOSE_RADIUS_COMPENSATION",
    "FINISHING_VOLUME_REQUIRES_PRECUT_STOCK_MODEL",
)
GROOVING_WARNINGS = REVIEW_WARNINGS + (
    "GROOVE_PLUNGES_INCLUDE_FULL_RADIAL_RELIEF_RETRACT",
    "GROOVE_TOOL_WIDTH_AND_CORNER_RADIUS_REQUIRE_HUMAN_REVIEW",
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
        material_removal_volume_mm3=math.fsum(item.estimated_removed_volume_mm3 for item in passes),
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
        material_removal_volume_mm3=math.fsum(item.estimated_removed_volume_mm3 for item in passes),
        warnings=REVIEW_WARNINGS,
    )


def _finishing_contour(request: TurningStrategyPlanRequest) -> tuple[RzPoint, ...]:
    """Return the exposed front-to-rear profile without the axis closure."""
    tolerance = request.linear_tolerance_mm
    points = request.profile_data
    surface_indices = [
        index
        for index, point in enumerate(points)
        if point.r_mm > tolerance
        and (
            math.isclose(
                point.z_mm,
                request.bounding_box.max_z_mm,
                abs_tol=tolerance,
                rel_tol=0,
            )
            or math.isclose(
                point.z_mm,
                request.bounding_box.min_z_mm,
                abs_tol=tolerance,
                rel_tol=0,
            )
        )
    ]
    if len(surface_indices) < 2:
        raise TurningStrategyValidationError("FINISHING_CONTOUR_BOUNDARIES_MISSING")

    start, end = min(surface_indices), max(surface_indices)
    contour = tuple(points[start : end + 1])
    if contour[0].z_mm < contour[-1].z_mm:
        contour = tuple(reversed(contour))
    if not math.isclose(
        contour[0].z_mm,
        request.bounding_box.max_z_mm,
        abs_tol=tolerance,
        rel_tol=0,
    ) or not math.isclose(
        contour[-1].z_mm,
        request.bounding_box.min_z_mm,
        abs_tol=tolerance,
        rel_tol=0,
    ):
        raise TurningStrategyValidationError("FINISHING_CONTOUR_INCOMPLETE")
    if any(point.r_mm <= tolerance for point in contour):
        raise TurningStrategyValidationError("FINISHING_CONTOUR_TOUCHES_AXIS")
    if any(
        following.z_mm > current.z_mm + tolerance
        for current, following in zip(contour, contour[1:])
    ):
        raise TurningStrategyValidationError("FINISHING_CONTOUR_REQUIRES_REAR_APPROACH")
    return contour


def _unit_tangent(first: RzPoint, second: RzPoint) -> tuple[float, float]:
    delta_r = second.r_mm - first.r_mm
    delta_z = second.z_mm - first.z_mm
    length = math.hypot(delta_r, delta_z)
    if length <= 0:
        raise TurningStrategyValidationError("FINISHING_CONTOUR_HAS_DEGENERATE_SEGMENT")
    return delta_r / length, delta_z / length


def _circumradius(
    first: RzPoint,
    middle: RzPoint,
    last: RzPoint,
) -> float:
    first_length = math.hypot(
        middle.r_mm - first.r_mm,
        middle.z_mm - first.z_mm,
    )
    second_length = math.hypot(
        last.r_mm - middle.r_mm,
        last.z_mm - middle.z_mm,
    )
    chord = math.hypot(last.r_mm - first.r_mm, last.z_mm - first.z_mm)
    twice_area = abs(
        (middle.r_mm - first.r_mm) * (last.z_mm - middle.z_mm)
        - (middle.z_mm - first.z_mm) * (last.r_mm - middle.r_mm)
    )
    if twice_area <= 1e-15:
        return math.inf
    return first_length * second_length * chord / (2.0 * twice_area)


def _validate_finishing_clearance(
    request: TurningStrategyPlanRequest,
    contour: tuple[RzPoint, ...],
) -> None:
    """Reject concave profile curvature that the round tool nose cannot enter."""
    tool_radius = request.tool.tip_radius_mm
    tolerance = request.linear_tolerance_mm
    edge_projection = abs(math.sin(math.radians(request.tool.cutting_edge_angle_deg)))
    effective_edge_reach = request.tool.cutting_edge_length_mm * edge_projection
    required_reach = tool_radius + request.finish_allowance_mm
    if required_reach > effective_edge_reach + tolerance:
        raise TurningStrategyValidationError("TOOL_GEOMETRY_UNDERCUT_COLLISION")
    for first, middle, last in zip(contour, contour[1:], contour[2:]):
        before = _unit_tangent(first, middle)
        after = _unit_tangent(middle, last)
        signed_turn = before[0] * after[1] - before[1] * after[0]
        if signed_turn >= -tolerance:
            continue
        local_radius = _circumradius(first, middle, last)
        if tool_radius > local_radius + tolerance:
            raise TurningStrategyValidationError("TOOL_GEOMETRY_UNDERCUT_COLLISION")


def _offset_vertex(
    point: RzPoint,
    previous_tangent: tuple[float, float] | None,
    following_tangent: tuple[float, float] | None,
    offset_mm: float,
    tolerance: float,
) -> RzPoint:
    tangents = tuple(
        tangent for tangent in (previous_tangent, following_tangent) if tangent is not None
    )
    normals = tuple((-tangent[1], tangent[0]) for tangent in tangents)
    if len(normals) == 1:
        direction_r, direction_z = normals[0]
        scale = offset_mm
    else:
        summed_r = normals[0][0] + normals[1][0]
        summed_z = normals[0][1] + normals[1][1]
        length = math.hypot(summed_r, summed_z)
        if length <= tolerance:
            raise TurningStrategyValidationError("FINISHING_OFFSET_REVERSAL")
        direction_r, direction_z = summed_r / length, summed_z / length
        projection = direction_r * normals[1][0] + direction_z * normals[1][1]
        if projection <= tolerance:
            raise TurningStrategyValidationError("FINISHING_OFFSET_INTERFERENCE")
        scale = offset_mm / projection
    compensated_r = point.r_mm + direction_r * scale
    compensated_z = point.z_mm + direction_z * scale
    if compensated_r < -tolerance:
        raise TurningStrategyValidationError("FINISHING_OFFSET_NEGATIVE_RADIUS")
    return RzPoint(r_mm=max(0.0, compensated_r), z_mm=compensated_z)


def _plan_finishing(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    contour = _finishing_contour(request)
    _validate_finishing_clearance(request, contour)
    tangents = tuple(_unit_tangent(first, second) for first, second in zip(contour, contour[1:]))
    offset = request.tool.tip_radius_mm + request.finish_allowance_mm
    compensated = tuple(
        _offset_vertex(
            point,
            tangents[index - 1] if index else None,
            tangents[index] if index < len(tangents) else None,
            offset,
            request.linear_tolerance_mm,
        )
        for index, point in enumerate(contour)
    )
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.FINISHING,
        passes=(
            MachiningPass(
                sequence=1,
                operation_type=TurningOperationType.FINISHING,
                coordinates_rz_mm=compensated,
                estimated_removed_volume_mm3=0.0,
            ),
        ),
        material_removal_volume_mm3=0.0,
        warnings=FINISHING_WARNINGS,
    )


def _groove_spans(request: TurningStrategyPlanRequest) -> tuple[_AxialSpan, ...]:
    """Find axial groove floors bounded by a larger-radius shoulder at each end."""
    contour = _finishing_contour(request)
    tolerance = request.linear_tolerance_mm
    grooves: list[_AxialSpan] = []
    for index, (first, second) in enumerate(zip(contour, contour[1:])):
        if index == 0 or index + 2 >= len(contour):
            continue
        if not math.isclose(first.r_mm, second.r_mm, abs_tol=tolerance, rel_tol=0):
            continue
        if abs(first.z_mm - second.z_mm) <= tolerance:
            continue
        previous = contour[index - 1]
        following = contour[index + 2]
        if previous.r_mm <= first.r_mm + tolerance or following.r_mm <= first.r_mm + tolerance:
            continue
        grooves.append(
            _AxialSpan(
                radius_mm=first.r_mm,
                front_z_mm=max(first.z_mm, second.z_mm),
                rear_z_mm=min(first.z_mm, second.z_mm),
            )
        )
    if not grooves:
        raise TurningStrategyValidationError("GROOVE_PROFILE_NOT_FOUND")
    return tuple(grooves)


def _groove_centers(
    groove: _AxialSpan,
    insert_width_mm: float,
    corner_radius_mm: float,
    tolerance: float,
) -> tuple[float, ...]:
    if groove.length_mm + tolerance < insert_width_mm:
        raise TurningStrategyValidationError("GROOVE_NARROWER_THAN_INSERT")
    if corner_radius_mm * 2 >= insert_width_mm - tolerance:
        raise TurningStrategyValidationError("GROOVE_INSERT_CORNER_RADIUS_INVALID")

    front = groove.front_z_mm - insert_width_mm / 2
    rear = groove.rear_z_mm + insert_width_mm / 2
    available_travel = front - rear
    if available_travel <= tolerance:
        return ((groove.front_z_mm + groove.rear_z_mm) / 2,)

    maximum_stepover = insert_width_mm - 2 * corner_radius_mm
    interval_count = math.ceil(available_travel / maximum_stepover)
    return tuple(
        front - available_travel * index / interval_count for index in range(interval_count + 1)
    )


def _plan_grooving(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    insert_width = request.tool.insert_width_mm
    if insert_width is None:
        raise TurningStrategyValidationError("GROOVING_INSERT_WIDTH_REQUIRED")

    grooves = _groove_spans(request)
    passes: list[MachiningPass] = []
    for groove in grooves:
        centers = _groove_centers(
            groove,
            insert_width,
            request.tool.tip_radius_mm,
            request.linear_tolerance_mm,
        )
        contour = _finishing_contour(request)
        floor_index = next(
            index
            for index, (first, second) in enumerate(zip(contour, contour[1:]))
            if math.isclose(
                first.r_mm,
                groove.radius_mm,
                abs_tol=request.linear_tolerance_mm,
                rel_tol=0,
            )
            and math.isclose(
                max(first.z_mm, second.z_mm),
                groove.front_z_mm,
                abs_tol=request.linear_tolerance_mm,
                rel_tol=0,
            )
            and math.isclose(
                min(first.z_mm, second.z_mm),
                groove.rear_z_mm,
                abs_tol=request.linear_tolerance_mm,
                rel_tol=0,
            )
        )
        entry_radius = min(contour[floor_index - 1].r_mm, contour[floor_index + 2].r_mm)
        if entry_radius > request.stock_radius_mm + request.linear_tolerance_mm:
            raise TurningStrategyValidationError("GROOVE_PLUNGE_OUTSIDE_STOCK_ENVELOPE")
        radial_levels = _levels(
            entry_radius,
            groove.radius_mm,
            request.cutting_parameters.depth_of_cut_mm,
        )
        if len(passes) + len(centers) * len(radial_levels) > MAX_PASSES:
            raise TurningStrategyValidationError("PASS_LIMIT_EXCEEDED")

        allocated_width = groove.length_mm / len(centers)
        previous_radius = entry_radius
        for radius in radial_levels:
            removed_per_center = math.pi * (previous_radius**2 - radius**2) * allocated_width
            for center_z in centers:
                passes.append(
                    MachiningPass(
                        sequence=len(passes) + 1,
                        operation_type=TurningOperationType.GROOVING,
                        coordinates_rz_mm=(
                            RzPoint(r_mm=entry_radius, z_mm=center_z),
                            RzPoint(r_mm=radius, z_mm=center_z),
                            RzPoint(r_mm=entry_radius, z_mm=center_z),
                        ),
                        estimated_removed_volume_mm3=removed_per_center,
                    )
                )
            previous_radius = radius

    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.GROOVING,
        passes=tuple(passes),
        material_removal_volume_mm3=math.fsum(item.estimated_removed_volume_mm3 for item in passes),
        warnings=GROOVING_WARNINGS,
    )


def plan_turning_strategy(request: TurningStrategyPlanRequest) -> TurningStrategyPlanResponse:
    """Build a deterministic review-only 2D plan without machine or NC authority."""
    _validate_profile(request)
    if request.operation_type == TurningOperationType.FACING:
        return _plan_facing(request)
    if request.operation_type == TurningOperationType.ROUGH_TURNING:
        return _plan_roughing(request)
    if request.operation_type == TurningOperationType.FINISHING:
        return _plan_finishing(request)
    if request.operation_type == TurningOperationType.GROOVING:
        return _plan_grooving(request)
    raise TurningStrategyValidationError("OPERATION_NOT_IMPLEMENTED_IN_FOUNDATION")
