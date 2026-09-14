"""Analytical three-jaw chuck clamping audit for review-only CNC reports."""

import math
from typing import Literal

from app.modules.cnc.schemas import WorkholdingClampingAuditPayload


class WorkholdingAuditError(ValueError):
    """Stable fail-closed reason for invalid analytical workholding inputs."""


def _finite(value: float, *, code: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise WorkholdingAuditError(code)
    return float(value)


def audit_workholding_clamping(
    *,
    static_clamping_force_per_jaw_n: float,
    jaw_mass_kg: float,
    center_of_mass_radius_mm: float,
    operating_rpm: float,
    maximum_declared_rpm: float,
    axial_cutting_force_n: float,
    friction_coefficient: float,
    required_safety_factor: float = 2.0,
) -> WorkholdingClampingAuditPayload:
    """Estimate centrifugal clamping loss and axial slip safety for three jaws."""
    static_force = _finite(
        static_clamping_force_per_jaw_n,
        code="WORKHOLDING_STATIC_CLAMPING_FORCE_INVALID",
    )
    jaw_mass = _finite(jaw_mass_kg, code="WORKHOLDING_JAW_MASS_INVALID")
    radius_mm = _finite(
        center_of_mass_radius_mm,
        code="WORKHOLDING_CENTER_OF_MASS_RADIUS_INVALID",
    )
    rpm = _finite(operating_rpm, code="WORKHOLDING_OPERATING_RPM_INVALID")
    rpm_limit = _finite(maximum_declared_rpm, code="WORKHOLDING_MAXIMUM_RPM_INVALID")
    axial_force = _finite(axial_cutting_force_n, code="WORKHOLDING_AXIAL_FORCE_INVALID")
    friction = _finite(friction_coefficient, code="WORKHOLDING_FRICTION_INVALID")
    required_factor = _finite(
        required_safety_factor,
        code="WORKHOLDING_REQUIRED_SAFETY_FACTOR_INVALID",
    )

    if not 0 < static_force <= 2_000_000:
        raise WorkholdingAuditError("WORKHOLDING_STATIC_CLAMPING_FORCE_INVALID")
    if not 0.01 <= jaw_mass <= 50:
        raise WorkholdingAuditError("WORKHOLDING_JAW_MASS_INVALID")
    if not 1 <= radius_mm <= 1_000:
        raise WorkholdingAuditError("WORKHOLDING_CENTER_OF_MASS_RADIUS_INVALID")
    if not 0 < rpm_limit <= 50_000:
        raise WorkholdingAuditError("WORKHOLDING_MAXIMUM_RPM_INVALID")
    if not 0 < rpm <= rpm_limit:
        raise WorkholdingAuditError("WORKHOLDING_OPERATING_RPM_EXCEEDS_DECLARED_LIMIT")
    if not 0 < axial_force <= 10_000_000:
        raise WorkholdingAuditError("WORKHOLDING_AXIAL_FORCE_INVALID")
    if not 0 < friction <= 1:
        raise WorkholdingAuditError("WORKHOLDING_FRICTION_OUTSIDE_PHYSICAL_LIMITS")
    if not 2 <= required_factor <= 100:
        raise WorkholdingAuditError("WORKHOLDING_REQUIRED_SAFETY_FACTOR_INVALID")

    angular_velocity_rad_s = 2.0 * math.pi * rpm / 60.0
    centrifugal_force_per_jaw_n = (
        jaw_mass * (radius_mm / 1_000.0) * angular_velocity_rad_s**2
    )
    total_centrifugal_loss_n = 3.0 * centrifugal_force_per_jaw_n
    dynamic_clamping_force_total_n = 3.0 * static_force - total_centrifugal_loss_n
    if not math.isfinite(dynamic_clamping_force_total_n):
        raise WorkholdingAuditError("WORKHOLDING_ESTIMATE_NON_CONVERGENT")
    if dynamic_clamping_force_total_n <= 0:
        raise WorkholdingAuditError("WORKHOLDING_TOTAL_CLAMPING_LOSS")

    friction_resistance_n = friction * dynamic_clamping_force_total_n
    clamping_safety_factor = friction_resistance_n / axial_force
    if not all(
        math.isfinite(value) and value > 0
        for value in (
            centrifugal_force_per_jaw_n,
            total_centrifugal_loss_n,
            friction_resistance_n,
            clamping_safety_factor,
        )
    ):
        raise WorkholdingAuditError("WORKHOLDING_ESTIMATE_NON_CONVERGENT")
    status: Literal[
        "DYNAMIC_CLAMPING_SAFE",
        "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING",
    ] = (
        "DYNAMIC_CLAMPING_SAFE"
        if clamping_safety_factor >= required_factor
        else "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING"
    )
    return WorkholdingClampingAuditPayload(
        static_clamping_force_per_jaw_n=static_force,
        jaw_mass_kg=jaw_mass,
        center_of_mass_radius_mm=radius_mm,
        operating_rpm=rpm,
        maximum_declared_rpm=rpm_limit,
        axial_cutting_force_n=axial_force,
        friction_coefficient=friction,
        required_safety_factor=required_factor,
        centrifugal_force_per_jaw_n=centrifugal_force_per_jaw_n,
        total_centrifugal_loss_n=total_centrifugal_loss_n,
        dynamic_clamping_force_total_n=dynamic_clamping_force_total_n,
        friction_resistance_n=friction_resistance_n,
        clamping_safety_factor=clamping_safety_factor,
        clamping_status=status,
    )


__all__ = ("WorkholdingAuditError", "audit_workholding_clamping")
