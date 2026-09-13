from __future__ import annotations

import re
from dataclasses import dataclass
from math import hypot
from typing import Literal

from app.modules.cnc.enums import CNCControllerType
from app.modules.cnc.schemas import (
    ChuckExclusionZone2D,
    ChuckProximityAudit,
    MachineEnvelope2D,
    ToolpathSegment2D,
    ToolpathSimulationPayload,
    TurningStock2D,
)
from app.modules.cnc.services.envelope_validator import validate_kinematic_envelope


_MOTION_CODES: dict[str, Literal["RAPID", "LINEAR"]] = {
    "G0": "RAPID",
    "G00": "RAPID",
    "G1": "LINEAR",
    "G01": "LINEAR",
}
_COORDINATE_WORD = re.compile(r"([XZ])([+-]?(?:\d+(?:\.\d*)?|\.\d+))")
_FEED_WORD = re.compile(r"F([+]?(?:\d+(?:\.\d*)?|\.\d+))")
_FANUC_TOOL_WORD = re.compile(r"T(\d{2,4})")
_SIEMENS_TOOL = re.compile(r'T="([A-Za-z0-9 _-]+)"(?:\s+D(\d{1,2}))?')
_PARENTHESIZED_COMMENT = re.compile(r"\([^)]*\)")
_CHUCK_PROXIMITY_THRESHOLD_MM = 5.0


class ToolpathSimulationError(ValueError):
    """Stable failure for ISO programs that cannot be simulated deterministically."""


@dataclass(frozen=True, slots=True)
class _Point2D:
    x_mm: float
    z_mm: float


def _orientation(first: _Point2D, second: _Point2D, third: _Point2D) -> float:
    return (second.x_mm - first.x_mm) * (third.z_mm - first.z_mm) - (
        second.z_mm - first.z_mm
    ) * (third.x_mm - first.x_mm)


def _on_segment(point: _Point2D, start: _Point2D, end: _Point2D) -> bool:
    return (
        min(start.x_mm, end.x_mm) <= point.x_mm <= max(start.x_mm, end.x_mm)
        and min(start.z_mm, end.z_mm) <= point.z_mm <= max(start.z_mm, end.z_mm)
    )


def _segments_intersect(
    first_start: _Point2D,
    first_end: _Point2D,
    second_start: _Point2D,
    second_end: _Point2D,
) -> bool:
    orientations = (
        _orientation(first_start, first_end, second_start),
        _orientation(first_start, first_end, second_end),
        _orientation(second_start, second_end, first_start),
        _orientation(second_start, second_end, first_end),
    )
    if orientations[0] * orientations[1] < 0 and orientations[2] * orientations[3] < 0:
        return True
    return any(
        orientation == 0 and _on_segment(point, start, end)
        for orientation, point, start, end in (
            (orientations[0], second_start, first_start, first_end),
            (orientations[1], second_end, first_start, first_end),
            (orientations[2], first_start, second_start, second_end),
            (orientations[3], first_end, second_start, second_end),
        )
    )


def _point_to_segment_distance(point: _Point2D, start: _Point2D, end: _Point2D) -> float:
    delta_x = end.x_mm - start.x_mm
    delta_z = end.z_mm - start.z_mm
    squared_length = delta_x * delta_x + delta_z * delta_z
    if squared_length == 0:
        return hypot(point.x_mm - start.x_mm, point.z_mm - start.z_mm)
    projection = max(
        0.0,
        min(
            1.0,
            ((point.x_mm - start.x_mm) * delta_x + (point.z_mm - start.z_mm) * delta_z)
            / squared_length,
        ),
    )
    return hypot(
        point.x_mm - (start.x_mm + projection * delta_x),
        point.z_mm - (start.z_mm + projection * delta_z),
    )


def _segment_distance(
    first_start: _Point2D,
    first_end: _Point2D,
    second_start: _Point2D,
    second_end: _Point2D,
) -> float:
    if _segments_intersect(first_start, first_end, second_start, second_end):
        return 0.0
    return min(
        _point_to_segment_distance(first_start, second_start, second_end),
        _point_to_segment_distance(first_end, second_start, second_end),
        _point_to_segment_distance(second_start, first_start, first_end),
        _point_to_segment_distance(second_end, first_start, first_end),
    )


def audit_chuck_proximity(
    segments: tuple[ToolpathSegment2D, ...],
    chuck_zone: ChuckExclusionZone2D,
    *,
    threshold_mm: float = _CHUCK_PROXIMITY_THRESHOLD_MM,
) -> ChuckProximityAudit:
    """Return the deterministic minimum path clearance from the chuck boundary."""
    corners = (
        _Point2D(chuck_zone.x_min_mm, chuck_zone.z_min_mm),
        _Point2D(chuck_zone.x_max_mm, chuck_zone.z_min_mm),
        _Point2D(chuck_zone.x_max_mm, chuck_zone.z_max_mm),
        _Point2D(chuck_zone.x_min_mm, chuck_zone.z_max_mm),
    )
    boundary_edges = tuple(zip(corners, corners[1:] + corners[:1], strict=True))
    closest_segment_index = 0
    minimum_clearance = float("inf")
    for index, segment in enumerate(segments):
        start = _Point2D(segment.x_start_mm, segment.z_start_mm)
        end = _Point2D(segment.x_end_mm, segment.z_end_mm)
        clearance = min(
            _segment_distance(start, end, edge_start, edge_end)
            for edge_start, edge_end in boundary_edges
        )
        if clearance < minimum_clearance:
            minimum_clearance = clearance
            closest_segment_index = index

    minimum_clearance = round(minimum_clearance, 9)
    warning_code: Literal["WARNING_PROXIMITY_CHUCK"] | None = (
        "WARNING_PROXIMITY_CHUCK" if minimum_clearance < threshold_mm else None
    )
    return ChuckProximityAudit(
        minimum_clearance_mm=minimum_clearance,
        threshold_mm=threshold_mm,
        closest_segment_index=closest_segment_index,
        warning_code=warning_code,
    )


def _tool_from_line(line: str, current: str | None) -> str | None:
    siemens = _SIEMENS_TOOL.search(line)
    if siemens is not None:
        name, offset = siemens.groups()
        return name if offset is None else f'{name}/D{offset}'
    for word in line.split():
        fanuc = _FANUC_TOOL_WORD.fullmatch(word)
        if fanuc is not None:
            return f"T{fanuc.group(1)}"
    return current


def parse_toolpath_simulation(
    program_text: str,
    *,
    controller_profile: CNCControllerType,
    machine_envelope: MachineEnvelope2D,
    stock: TurningStock2D,
    source_plan_id: str | None = None,
) -> ToolpathSimulationPayload:
    """Convert an envelope-safe ISO turning program into deterministic 2D segments."""
    validate_kinematic_envelope(program_text, machine_envelope)

    current: _Point2D | None = None
    active_tool: str | None = None
    modal_feed: float | None = None
    segments: list[ToolpathSegment2D] = []

    for raw_line in program_text.splitlines():
        line = _PARENTHESIZED_COMMENT.sub("", raw_line).strip().upper()
        if not line:
            continue
        active_tool = _tool_from_line(line, active_tool)
        words = line.split()
        motion_words = [word for word in words if word in _MOTION_CODES]
        if not motion_words:
            continue
        if len(motion_words) != 1:
            raise ToolpathSimulationError("AMBIGUOUS_MOTION_BLOCK")

        coordinates: dict[str, float] = {}
        for word in words:
            if word.startswith(("X", "Z")):
                match = _COORDINATE_WORD.fullmatch(word)
                if match is None:
                    raise ToolpathSimulationError("MALFORMED_MOTION_COORDINATE")
                axis, raw_value = match.groups()
                if axis in coordinates:
                    raise ToolpathSimulationError("DUPLICATE_MOTION_COORDINATE")
                coordinates[axis] = float(raw_value)
            elif word.startswith("F"):
                match = _FEED_WORD.fullmatch(word)
                if match is None or float(match.group(1)) <= 0:
                    raise ToolpathSimulationError("INVALID_FEED_VALUE")
                modal_feed = float(match.group(1))

        if current is None:
            if set(coordinates) != {"X", "Z"}:
                raise ToolpathSimulationError("INCOMPLETE_INITIAL_MOTION_COORDINATES")
            current = _Point2D(x_mm=coordinates["X"], z_mm=coordinates["Z"])
            continue

        target = _Point2D(
            x_mm=coordinates.get("X", current.x_mm),
            z_mm=coordinates.get("Z", current.z_mm),
        )
        motion_type = _MOTION_CODES[motion_words[0]]
        segments.append(
            ToolpathSegment2D(
                motion_type=motion_type,
                x_start_mm=current.x_mm,
                z_start_mm=current.z_mm,
                x_end_mm=target.x_mm,
                z_end_mm=target.z_mm,
                feed=modal_feed if motion_type == "LINEAR" else None,
                active_tool=active_tool,
            )
        )
        current = target

    if not segments:
        raise ToolpathSimulationError("INSUFFICIENT_TOOLPATH_POINTS")

    segment_tuple = tuple(segments)
    return ToolpathSimulationPayload(
        source_plan_id=source_plan_id,
        controller_profile=controller_profile,
        segments=segment_tuple,
        machine_envelope=machine_envelope,
        stock=stock,
        chuck_proximity=audit_chuck_proximity(
            segment_tuple,
            machine_envelope.chuck_exclusion_zone,
        ),
    )
