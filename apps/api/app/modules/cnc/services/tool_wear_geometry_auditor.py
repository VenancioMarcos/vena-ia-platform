"""Progressive insert-wear geometry audit without CNC offset authority."""

import math
from typing import Literal

from app.modules.cnc.schemas import ToolLifeTaylorAuditPayload, ToolWearGeometryAuditPayload


def audit_tool_wear_geometry(
    tool_life_audit: ToolLifeTaylorAuditPayload,
    *,
    nominal_nose_radius_mm: float,
    maximum_allowable_flank_wear_vb_mm: float = 0.3,
    clearance_angle_deg: float = 7.0,
    position_angle_deg: float = 95.0,
    geometry_tolerance_um: float,
) -> ToolWearGeometryAuditPayload:
    source = ToolLifeTaylorAuditPayload.model_validate(tool_life_audit)
    values = (
        nominal_nose_radius_mm,
        maximum_allowable_flank_wear_vb_mm,
        geometry_tolerance_um,
    )
    if any(isinstance(value, bool) or not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("TOOL_WEAR_GEOMETRY_INPUT_INVALID")
    if not math.isfinite(clearance_angle_deg) or not 0 < clearance_angle_deg < 90:
        raise ValueError("TOOL_WEAR_CLEARANCE_ANGLE_INVALID")
    if (
        not math.isfinite(position_angle_deg)
        or not 0 < position_angle_deg < 180
        or math.isclose(position_angle_deg, 90)
    ):
        raise ValueError("TOOL_WEAR_POSITION_ANGLE_INVALID")
    progress = source.tool_life_consumed_percent
    wear = maximum_allowable_flank_wear_vb_mm * math.sqrt(progress / 100.0)
    radial_mm = wear * math.tan(math.radians(clearance_angle_deg))
    effective_position = min(position_angle_deg, 180.0 - position_angle_deg)
    axial_mm = radial_mm / math.tan(math.radians(effective_position))
    status: Literal[
        "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE",
        "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING",
    ] = (
        "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING"
        if radial_mm * 1_000 > geometry_tolerance_um * 0.5
        else "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE"
    )
    return ToolWearGeometryAuditPayload(
        source_tool_life_audit=source,
        nominal_nose_radius_mm=nominal_nose_radius_mm,
        clearance_angle_deg=clearance_angle_deg,
        position_angle_deg=position_angle_deg,
        maximum_allowable_flank_wear_vb_mm=maximum_allowable_flank_wear_vb_mm,
        estimated_flank_wear_vb_mm=wear,
        flank_wear_progress_percent=progress,
        effective_nose_radius_mm=nominal_nose_radius_mm + radial_mm / 2.0,
        predicted_radial_deviation_um=radial_mm * 1_000.0,
        predicted_axial_deviation_um=axial_mm * 1_000.0,
        geometry_tolerance_um=geometry_tolerance_um,
        audit_status=status,
    )


__all__ = ("audit_tool_wear_geometry",)
