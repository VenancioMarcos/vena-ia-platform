from __future__ import annotations

import math
import re
from dataclasses import dataclass

from app.modules.cnc.schemas import ChuckExclusionZone2D, MachineEnvelope2D


MOTION_CODES = frozenset({"G0", "G00", "G1", "G01"})
_COORDINATE_WORD = re.compile(r"([XZ])([+-]?(?:\d+(?:\.\d*)?|\.\d+))")
_PARENTHESIZED_COMMENT = re.compile(r"\([^)]*\)")


class KinematicBoundaryViolation(ValueError):
    """Stable fail-closed failure for an unsafe or unverifiable 2D motion."""


@dataclass(frozen=True, slots=True)
class _Point2D:
    x_mm: float
    z_mm: float


def _is_inside_zone(point: _Point2D, zone: ChuckExclusionZone2D) -> bool:
    return (
        zone.x_min_mm <= point.x_mm <= zone.x_max_mm
        and zone.z_min_mm <= point.z_mm <= zone.z_max_mm
    )


def _segment_intersects_zone(
    start: _Point2D,
    end: _Point2D,
    zone: ChuckExclusionZone2D,
) -> bool:
    """Return whether a closed segment touches the closed rectangular zone."""
    delta_x = end.x_mm - start.x_mm
    delta_z = end.z_mm - start.z_mm
    lower = 0.0
    upper = 1.0
    for direction, distance in (
        (-delta_x, start.x_mm - zone.x_min_mm),
        (delta_x, zone.x_max_mm - start.x_mm),
        (-delta_z, start.z_mm - zone.z_min_mm),
        (delta_z, zone.z_max_mm - start.z_mm),
    ):
        if math.isclose(direction, 0.0, abs_tol=1e-12):
            if distance < 0:
                return False
            continue
        ratio = distance / direction
        if direction < 0:
            lower = max(lower, ratio)
        else:
            upper = min(upper, ratio)
        if lower > upper:
            return False
    return True


def _validate_travel(point: _Point2D, envelope: MachineEnvelope2D) -> None:
    if not envelope.x_min_mm <= point.x_mm <= envelope.x_max_mm:
        raise KinematicBoundaryViolation("X_AXIS_TRAVEL_LIMIT_EXCEEDED")
    if not envelope.z_min_mm <= point.z_mm <= envelope.z_max_mm:
        raise KinematicBoundaryViolation("Z_AXIS_TRAVEL_LIMIT_EXCEEDED")


def validate_kinematic_envelope(program_text: str, envelope: MachineEnvelope2D) -> int:
    """Validate every ISO G0/G1 point and segment against a 2D machine envelope."""
    current: _Point2D | None = None
    validated_blocks = 0

    for raw_line in program_text.splitlines():
        line = _PARENTHESIZED_COMMENT.sub("", raw_line).strip().upper()
        if not line:
            continue
        words = line.split()
        if not any(word in MOTION_CODES for word in words):
            continue

        coordinates: dict[str, float] = {}
        for word in words:
            if not word.startswith(("X", "Z")):
                continue
            match = _COORDINATE_WORD.fullmatch(word)
            if match is None:
                raise KinematicBoundaryViolation("MALFORMED_MOTION_COORDINATE")
            axis, raw_value = match.groups()
            if axis in coordinates:
                raise KinematicBoundaryViolation("DUPLICATE_MOTION_COORDINATE")
            coordinates[axis] = float(raw_value)

        if not coordinates:
            raise KinematicBoundaryViolation("MOTION_BLOCK_WITHOUT_COORDINATES")
        if current is None and set(coordinates) != {"X", "Z"}:
            raise KinematicBoundaryViolation("INCOMPLETE_INITIAL_MOTION_COORDINATES")

        target = _Point2D(
            x_mm=coordinates.get("X", current.x_mm if current is not None else math.nan),
            z_mm=coordinates.get("Z", current.z_mm if current is not None else math.nan),
        )
        _validate_travel(target, envelope)
        if _is_inside_zone(target, envelope.chuck_exclusion_zone):
            raise KinematicBoundaryViolation("CHUCK_EXCLUSION_ZONE_VIOLATION")
        if current is not None and _segment_intersects_zone(
            current,
            target,
            envelope.chuck_exclusion_zone,
        ):
            raise KinematicBoundaryViolation("CHUCK_EXCLUSION_ZONE_VIOLATION")

        current = target
        validated_blocks += 1

    if validated_blocks == 0:
        raise KinematicBoundaryViolation("NO_VERIFIABLE_MOTION_BLOCKS")
    return validated_blocks
