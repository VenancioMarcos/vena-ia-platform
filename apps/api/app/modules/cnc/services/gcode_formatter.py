from __future__ import annotations

import math

from app.modules.cam.schemas import MachiningPass, RzPoint
from app.modules.cnc.enums import CNCControllerType, FeedMode, SpindleMode
from app.modules.cnc.schemas import (
    GCodeGenerationMetadata,
    GCodeGenerationRequest,
    GCodeGenerationResponse,
)
from app.modules.cnc.services.envelope_validator import validate_kinematic_envelope


SUPPORTED_CONTROLLERS = frozenset(CNCControllerType)
SAFETY_HEADER = (
    "(GOVERNANCE: PHYSICAL_USE_AUTHORIZED=FALSE)",
    "(GOVERNANCE: G9=PENDING_AUTHORITATIVE_REVIEW)",
    "(GOVERNANCE: NO_HUMAN_REVIEW_BYPASS=TRUE)",
    "(NOTICE: NON-EXECUTABLE AUDIT CODE ONLY)",
    "(SAFETY: PHYSICAL_USE_AUTHORIZED=FALSE)",
    "(SAFETY: G9=PENDING_AUTHORITATIVE_REVIEW)",
    "(SAFETY: NO_HUMAN_REVIEW_BYPASS=TRUE)",
    "(SAFETY: MACHINE_SEND=FALSE DNC=FALSE NC_TRANSFER=FALSE CYCLE_START=FALSE)",
    "(SAFETY: emission_status=CONTROLLER_PROFILE_UNRESOLVED)",
    "(SAFETY: executable_output=false)",
)


class GCodeFormattingError(ValueError):
    """Stable fail-closed failure for CNC candidate formatting."""


def _number(value: float) -> str:
    normalized = 0.0 if math.isclose(value, 0.0, abs_tol=5e-10) else value
    return f"{normalized:.6f}".rstrip("0").rstrip(".")


def _point_words(point: RzPoint) -> str:
    return f"X{_number(point.r_mm * 2.0)} Z{_number(point.z_mm)}"


def _path_length(path: tuple[RzPoint, ...]) -> float:
    return math.fsum(
        math.hypot((second.r_mm - first.r_mm) * 2.0, second.z_mm - first.z_mm)
        for first, second in zip(path, path[1:])
    )


def _pass_blocks(
    item: MachiningPass,
    feed_value: float,
    *,
    rapid_code: str = "G00",
    feed_code: str = "G01",
) -> list[str]:
    start, *remaining = item.coordinates_rz_mm
    blocks = [
        f"(PASS {item.sequence}: {item.operation_type.value})",
        f"{rapid_code} {_point_words(start)}",
    ]
    blocks.extend(
        f"{feed_code} {_point_words(point)} F{_number(feed_value)}" for point in remaining
    )
    return blocks


def _effective_feed_mm_min(request: GCodeGenerationRequest) -> float:
    if request.feed_mode is FeedMode.G94_PER_MINUTE:
        return request.feed_value
    spindle_rpm = (
        request.max_spindle_rpm
        if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED
        else request.spindle_value
    )
    return request.feed_value * spindle_rpm


def _estimated_seconds(request: GCodeGenerationRequest, path_length_mm: float) -> float:
    return path_length_mm / _effective_feed_mm_min(request) * 60.0


def _validate_machine_limits(request: GCodeGenerationRequest) -> None:
    effective_feed_mm_min = _effective_feed_mm_min(request)
    if effective_feed_mm_min > request.max_feed_mm_min:
        raise GCodeFormattingError("FEED_EXCEEDS_CONFIGURED_MACHINE_LIMIT")
    if (
        request.spindle_mode is SpindleMode.G97_DIRECT_RPM
        and request.spindle_value > request.max_spindle_rpm
    ):
        raise GCodeFormattingError("SPINDLE_SPEED_EXCEEDS_CONFIGURED_MACHINE_LIMIT")


def _fanuc_family_preamble(request: GCodeGenerationRequest) -> list[str]:
    tool_word = f"T{request.tool_number:02d}{request.tool_offset:02d}"
    spindle_code = (
        "G96" if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED else "G97"
    )
    blocks = [f"O{request.program_number}", tool_word, "G21", "G18"]
    blocks.append("G94" if request.feed_mode is FeedMode.G94_PER_MINUTE else "G95")
    if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED:
        blocks.append(f"G50 S{_number(request.max_spindle_rpm)}")
    blocks.append(f"{spindle_code} S{_number(request.spindle_value)}")
    return blocks


def _siemens_preamble(request: GCodeGenerationRequest) -> list[str]:
    spindle_code = (
        "G96" if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED else "G97"
    )
    blocks = [
        f"%_N_VENA_{request.program_number}_MPF",
        f'T="{request.tool_name}" D{request.tool_offset}',
        "G21",
        "G18",
        "G94" if request.feed_mode is FeedMode.G94_PER_MINUTE else "G95",
    ]
    if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED:
        blocks.append(f"LIMS={_number(request.max_spindle_rpm)}")
    blocks.append(f"{spindle_code} S{_number(request.spindle_value)}")
    return blocks


def _controller_preamble(request: GCodeGenerationRequest) -> list[str]:
    if request.controller_profile in (CNCControllerType.FANUC_0I, CNCControllerType.HAAS):
        return _fanuc_family_preamble(request)
    if request.controller_profile is CNCControllerType.SIEMENS_840D:
        return _siemens_preamble(request)
    return [
        f"O{request.program_number}",
        "G21",
        "G18",
        "G94" if request.feed_mode is FeedMode.G94_PER_MINUTE else "G95",
        (
            "G96" if request.spindle_mode is SpindleMode.G96_CONSTANT_SURFACE_SPEED else "G97"
        )
        + f" S{_number(request.spindle_value)}",
    ]


def format_gcode_candidate(request: GCodeGenerationRequest) -> GCodeGenerationResponse:
    """Format a deterministic, review-only ISO turning program candidate."""
    if request.controller_profile not in SUPPORTED_CONTROLLERS:
        raise GCodeFormattingError("UNSUPPORTED_CONTROLLER_PROFILE")
    if request.review_authentication != "AUTHENTICATED_REVIEW_CONTEXT":
        raise GCodeFormattingError("REVIEW_AUTHENTICATION_REQUIRED")
    if request.cam_plan_data.status != "PLANNED_REQUIRES_REVIEW":
        raise GCodeFormattingError("CAM_PLAN_NOT_REVIEWABLE")
    if request.cam_plan_data.executable_output or request.cam_plan_data.physical_use_authorized:
        raise GCodeFormattingError("CAM_PLAN_SAFETY_INVARIANT_VIOLATION")
    if request.cam_plan_data.g9_status != "PENDING_AUTHORITATIVE_REVIEW":
        raise GCodeFormattingError("CAM_PLAN_G9_INVARIANT_VIOLATION")
    if request.cam_plan_data.emission_status != "CONTROLLER_PROFILE_UNRESOLVED":
        raise GCodeFormattingError("CAM_PLAN_EMISSION_INVARIANT_VIOLATION")

    _validate_machine_limits(request)
    preamble = _controller_preamble(request)
    program_id, *modal_blocks = preamble
    lines = [
        program_id,
        f"(VENA_IA PLAN_ID={request.plan_id})",
        f"(CONTROLLER_PROFILE={request.controller_profile.value})",
        *SAFETY_HEADER,
        *modal_blocks,
    ]
    motion_codes = (
        {"rapid_code": "G0", "feed_code": "G1"}
        if request.controller_profile is CNCControllerType.SIEMENS_840D
        else {}
    )
    for item in request.cam_plan_data.passes:
        lines.extend(_pass_blocks(item, request.feed_value, **motion_codes))
    lines.extend(("M05", "M30", "%"))

    path_length_mm = math.fsum(_path_length(item.coordinates_rz_mm) for item in request.cam_plan_data.passes)
    motion_block_count = math.fsum(len(item.coordinates_rz_mm) for item in request.cam_plan_data.passes)
    program_text = "\n".join(lines)
    validate_kinematic_envelope(program_text, request.machine_envelope)
    return GCodeGenerationResponse(
        plan_id=request.plan_id,
        controller_profile=request.controller_profile,
        program_text=program_text,
        metadata=GCodeGenerationMetadata(
            path_length_mm=path_length_mm,
            estimated_cycle_time_seconds=_estimated_seconds(request, path_length_mm),
            motion_block_count=int(motion_block_count),
        ),
    )
