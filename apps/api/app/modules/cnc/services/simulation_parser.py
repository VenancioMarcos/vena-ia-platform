from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from app.modules.cnc.enums import CNCControllerType
from app.modules.cnc.schemas import (
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


class ToolpathSimulationError(ValueError):
    """Stable failure for ISO programs that cannot be simulated deterministically."""


@dataclass(frozen=True, slots=True)
class _Point2D:
    x_mm: float
    z_mm: float


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

    return ToolpathSimulationPayload(
        source_plan_id=source_plan_id,
        controller_profile=controller_profile,
        segments=tuple(segments),
        machine_envelope=machine_envelope,
        stock=stock,
    )
