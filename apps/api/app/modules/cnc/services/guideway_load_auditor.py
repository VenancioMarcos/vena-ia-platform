"""Analytical cutting-force, moment and guideway-block load audit."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import ValidationError

from app.modules.cnc.schemas import (
    GuidewayLoadAuditPayload,
    MachiningPowerForceAuditPayload,
)


class GuidewayLoadAuditError(ValueError):
    """Raised when a guideway load audit cannot be calculated safely."""


def _finite(value: float, *, code: str) -> float:
    if isinstance(value, bool):
        raise GuidewayLoadAuditError(code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise GuidewayLoadAuditError(code) from exc
    if not math.isfinite(number):
        raise GuidewayLoadAuditError(code)
    return number


def _positive(value: float, *, code: str, upper: float) -> float:
    number = _finite(value, code=code)
    if not 0 < number <= upper:
        raise GuidewayLoadAuditError(code)
    return number


def audit_guideway_load(
    source_power_force_audit: MachiningPowerForceAuditPayload,
    *,
    feed_force_ratio: float,
    radial_force_ratio: float,
    lever_arm_x_mm: float,
    lever_arm_y_mm: float,
    lever_arm_z_mm: float,
    block_spacing_x_mm: float,
    rail_spacing_y_mm: float,
    block_spacing_z_mm: float,
    static_capacity_n: float,
) -> GuidewayLoadAuditPayload:
    """Resolve conservative direct and moment reactions for four linear blocks."""

    try:
        power_force = MachiningPowerForceAuditPayload.model_validate(source_power_force_audit)
    except ValidationError as exc:
        raise GuidewayLoadAuditError("GUIDEWAY_KIENZLE_SOURCE_INVALID") from exc

    tangential_force = _positive(
        power_force.fc_nominal_n,
        code="GUIDEWAY_TANGENTIAL_FORCE_OUTSIDE_PHYSICAL_ENVELOPE",
        upper=10_000_000.0,
    )
    feed_ratio = _positive(
        feed_force_ratio,
        code="GUIDEWAY_FEED_FORCE_RATIO_INVALID",
        upper=2.0,
    )
    radial_ratio = _positive(
        radial_force_ratio,
        code="GUIDEWAY_RADIAL_FORCE_RATIO_INVALID",
        upper=2.0,
    )
    lever_x = _positive(
        lever_arm_x_mm,
        code="GUIDEWAY_LEVER_ARM_X_INVALID",
        upper=100_000.0,
    )
    lever_y = _positive(
        lever_arm_y_mm,
        code="GUIDEWAY_LEVER_ARM_Y_INVALID",
        upper=100_000.0,
    )
    lever_z = _positive(
        lever_arm_z_mm,
        code="GUIDEWAY_LEVER_ARM_Z_INVALID",
        upper=100_000.0,
    )
    spacing_x = _positive(
        block_spacing_x_mm,
        code="GUIDEWAY_BLOCK_SPACING_X_INVALID",
        upper=100_000.0,
    )
    spacing_y = _positive(
        rail_spacing_y_mm,
        code="GUIDEWAY_RAIL_SPACING_Y_INVALID",
        upper=100_000.0,
    )
    spacing_z = _positive(
        block_spacing_z_mm,
        code="GUIDEWAY_BLOCK_SPACING_Z_INVALID",
        upper=100_000.0,
    )
    capacity = _positive(
        static_capacity_n,
        code="GUIDEWAY_STATIC_CAPACITY_INVALID",
        upper=1_000_000_000.0,
    )

    axial_force = tangential_force * feed_ratio
    radial_force = tangential_force * radial_ratio
    for force, code in (
        (axial_force, "GUIDEWAY_AXIAL_FORCE_OUTSIDE_PHYSICAL_ENVELOPE"),
        (radial_force, "GUIDEWAY_RADIAL_FORCE_OUTSIDE_PHYSICAL_ENVELOPE"),
    ):
        if not 0 < force <= 10_000_000.0:
            raise GuidewayLoadAuditError(code)

    pitching_moment = (axial_force * lever_z + tangential_force * lever_x) / 1_000.0
    yawing_moment = (axial_force * lever_y + radial_force * lever_z) / 1_000.0
    rolling_moment = (radial_force * lever_y + tangential_force * lever_z) / 1_000.0
    direct_load_per_block = math.sqrt(tangential_force**2 + axial_force**2 + radial_force**2) / 4.0
    pitching_reaction = pitching_moment * 1_000.0 / (2.0 * spacing_z)
    yawing_reaction = yawing_moment * 1_000.0 / (2.0 * spacing_x)
    rolling_reaction = rolling_moment * 1_000.0 / (2.0 * spacing_y)
    max_block_load = direct_load_per_block + pitching_reaction + yawing_reaction + rolling_reaction
    load_ratio = max_block_load / capacity * 100.0
    status: Literal[
        "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING",
        "GUIDEWAY_LOAD_COMPLIANT",
    ] = (
        "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING"
        if max_block_load > 0.5 * capacity
        else "GUIDEWAY_LOAD_COMPLIANT"
    )

    return GuidewayLoadAuditPayload(
        source_power_force_audit=power_force,
        feed_force_ratio=feed_ratio,
        radial_force_ratio=radial_ratio,
        tangential_cutting_force_n=tangential_force,
        axial_feed_force_n=axial_force,
        radial_cutting_force_n=radial_force,
        lever_arm_x_mm=lever_x,
        lever_arm_y_mm=lever_y,
        lever_arm_z_mm=lever_z,
        block_spacing_x_mm=spacing_x,
        rail_spacing_y_mm=spacing_y,
        block_spacing_z_mm=spacing_z,
        pitching_moment_nm=pitching_moment,
        yawing_moment_nm=yawing_moment,
        rolling_moment_nm=rolling_moment,
        direct_load_per_block_n=direct_load_per_block,
        pitching_reaction_per_block_n=pitching_reaction,
        yawing_reaction_per_block_n=yawing_reaction,
        rolling_reaction_per_block_n=rolling_reaction,
        max_block_load_n=max_block_load,
        static_capacity_n=capacity,
        load_ratio_percent=load_ratio,
        guideway_status=status,
    )


__all__ = ("GuidewayLoadAuditError", "audit_guideway_load")
