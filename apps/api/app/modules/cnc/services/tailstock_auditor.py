"""Analytical tailstock support, deflection, and buckling audit."""

import math
from typing import Literal

from app.modules.cnc.schemas import TailstockThrustAuditPayload


class TailstockAuditError(ValueError):
    """Stable fail-closed reason for invalid analytical tailstock inputs."""


def _finite(value: float, *, code: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise TailstockAuditError(code)
    return float(value)


def audit_tailstock_thrust_deflection(
    *,
    tailstock_force_n: float,
    total_supported_length_mm: float,
    minimum_diameter_mm: float,
    cutting_load_position_mm: float,
    radial_cutting_force_n: float,
    young_modulus_mpa: float,
    engagement_z_coordinate_mm: float,
    effective_length_factor: float = 0.7,
) -> TailstockThrustAuditPayload:
    """Audit a fixed-pinned workpiece under radial cutting load and axial preload."""
    tailstock_force = _finite(tailstock_force_n, code="TAILSTOCK_FORCE_INVALID")
    length = _finite(
        total_supported_length_mm,
        code="TAILSTOCK_SUPPORTED_LENGTH_INVALID",
    )
    diameter = _finite(minimum_diameter_mm, code="TAILSTOCK_DIAMETER_INVALID")
    load_position = _finite(
        cutting_load_position_mm,
        code="TAILSTOCK_CUTTING_POSITION_INVALID",
    )
    radial_force = _finite(
        radial_cutting_force_n,
        code="TAILSTOCK_RADIAL_FORCE_INVALID",
    )
    young_modulus = _finite(young_modulus_mpa, code="TAILSTOCK_YOUNG_MODULUS_INVALID")
    engagement_z = _finite(
        engagement_z_coordinate_mm,
        code="TAILSTOCK_ENGAGEMENT_COORDINATE_REQUIRED",
    )
    length_factor = _finite(
        effective_length_factor,
        code="TAILSTOCK_EFFECTIVE_LENGTH_FACTOR_INVALID",
    )

    if not 0 < tailstock_force <= 10_000_000:
        raise TailstockAuditError("TAILSTOCK_FORCE_INVALID")
    if not 0 < length <= 100_000:
        raise TailstockAuditError("TAILSTOCK_SUPPORTED_LENGTH_INVALID")
    if not 0 < diameter <= 10_000:
        raise TailstockAuditError("TAILSTOCK_DIAMETER_INVALID")
    if not 0 < load_position < length:
        raise TailstockAuditError("TAILSTOCK_CUTTING_POSITION_OUTSIDE_SUPPORT_SPAN")
    if not 0 < radial_force <= 10_000_000:
        raise TailstockAuditError("TAILSTOCK_RADIAL_FORCE_INVALID")
    if not 0 < young_modulus <= 1_000_000:
        raise TailstockAuditError("TAILSTOCK_YOUNG_MODULUS_INVALID")
    if not 0 < length_factor <= 2:
        raise TailstockAuditError("TAILSTOCK_EFFECTIVE_LENGTH_FACTOR_INVALID")

    second_moment = math.pi * diameter**4 / 64.0
    distance_to_tailstock = length - load_position
    deflection_mm = (
        radial_force
        * load_position**2
        * distance_to_tailstock**2
        / (3.0 * young_modulus * second_moment * length)
    )
    critical_buckling_load = (
        math.pi**2
        * young_modulus
        * second_moment
        / (length_factor * length) ** 2
    )
    warning_threshold = 0.3 * critical_buckling_load
    results = (second_moment, deflection_mm, critical_buckling_load, warning_threshold)
    if any(not math.isfinite(value) or value <= 0 for value in results):
        raise TailstockAuditError("TAILSTOCK_ESTIMATE_NON_CONVERGENT")
    status: Literal[
        "TAILSTOCK_SUPPORT_COMPLIANT",
        "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING",
    ] = (
        "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING"
        if tailstock_force > warning_threshold
        else "TAILSTOCK_SUPPORT_COMPLIANT"
    )
    return TailstockThrustAuditPayload(
        tailstock_force_n=tailstock_force,
        critical_buckling_load_n=critical_buckling_load,
        max_supported_deflection_um=deflection_mm * 1_000.0,
        engagement_z_coordinate_mm=engagement_z,
        total_supported_length_mm=length,
        minimum_diameter_mm=diameter,
        cutting_load_position_mm=load_position,
        radial_cutting_force_n=radial_force,
        young_modulus_mpa=young_modulus,
        second_moment_area_mm4=second_moment,
        effective_length_factor=length_factor,
        warning_threshold_n=warning_threshold,
        tailstock_status=status,
    )


__all__ = ("TailstockAuditError", "audit_tailstock_thrust_deflection")
