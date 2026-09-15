"""Analytical ballscrew axial-thrust, buckling and critical-speed audit."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import ValidationError

from app.modules.cnc.schemas import (
    BallscrewAxialMechanicsAuditPayload,
    GuidewayLoadAuditPayload,
)


class BallscrewAuditError(ValueError):
    """Raised when ballscrew mechanics cannot be evaluated safely."""


def _finite(value: float, *, code: str) -> float:
    if isinstance(value, bool):
        raise BallscrewAuditError(code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BallscrewAuditError(code) from exc
    if not math.isfinite(number):
        raise BallscrewAuditError(code)
    return number


def _positive(value: float, *, code: str, upper: float) -> float:
    number = _finite(value, code=code)
    if not 0 < number <= upper:
        raise BallscrewAuditError(code)
    return number


def _nonnegative(value: float, *, code: str, upper: float) -> float:
    number = _finite(value, code=code)
    if not 0 <= number <= upper:
        raise BallscrewAuditError(code)
    return number


def audit_ballscrew_mechanics(
    source_guideway_load_audit: GuidewayLoadAuditPayload,
    *,
    guide_friction_coefficient: float,
    carriage_mass_kg: float,
    carriage_acceleration_m_s2: float,
    ballscrew_root_diameter_mm: float,
    ballscrew_lead_mm_per_rev: float,
    ballscrew_length_mm: float,
    young_modulus_mpa: float,
    buckling_mounting_factor: float,
    critical_speed_mounting_factor: float,
    axial_feed_rate_mm_per_min: float,
) -> BallscrewAxialMechanicsAuditPayload:
    """Resolve feed-axis thrust, Euler capacity and screw critical speed."""

    try:
        guideway = GuidewayLoadAuditPayload.model_validate(source_guideway_load_audit)
    except ValidationError as exc:
        raise BallscrewAuditError("BALLSCREW_GUIDEWAY_SOURCE_INVALID") from exc

    friction = _nonnegative(
        guide_friction_coefficient,
        code="BALLSCREW_GUIDE_FRICTION_INVALID",
        upper=1.0,
    )
    mass = _positive(
        carriage_mass_kg,
        code="BALLSCREW_CARRIAGE_MASS_INVALID",
        upper=1_000_000.0,
    )
    acceleration = _nonnegative(
        carriage_acceleration_m_s2,
        code="BALLSCREW_CARRIAGE_ACCELERATION_INVALID",
        upper=1_000.0,
    )
    root_diameter = _positive(
        ballscrew_root_diameter_mm,
        code="BALLSCREW_ROOT_DIAMETER_INVALID",
        upper=10_000.0,
    )
    lead = _positive(
        ballscrew_lead_mm_per_rev,
        code="BALLSCREW_LEAD_INVALID",
        upper=100_000.0,
    )
    length = _positive(
        ballscrew_length_mm,
        code="BALLSCREW_LENGTH_INVALID",
        upper=1_000_000.0,
    )
    modulus = _positive(
        young_modulus_mpa,
        code="BALLSCREW_YOUNG_MODULUS_INVALID",
        upper=1_000_000_000.0,
    )
    buckling_factor = _positive(
        buckling_mounting_factor,
        code="BALLSCREW_BUCKLING_MOUNTING_FACTOR_REQUIRED",
        upper=1_000.0,
    )
    speed_factor = _positive(
        critical_speed_mounting_factor,
        code="BALLSCREW_SPEED_MOUNTING_FACTOR_REQUIRED",
        upper=1_000.0,
    )
    axial_feed_rate = _nonnegative(
        axial_feed_rate_mm_per_min,
        code="BALLSCREW_AXIAL_FEED_RATE_INVALID",
        upper=100_000_000.0,
    )

    inertia = math.pi * root_diameter**4 / 64.0
    total_thrust = (
        guideway.axial_feed_force_n
        + friction * (mass * 9.80665 + guideway.radial_cutting_force_n)
        + mass * acceleration
    )
    buckling_limit = buckling_factor * math.pi**2 * modulus * inertia / length**2
    critical_speed = speed_factor * (root_diameter / length**2) * 10_000_000.0
    operating_speed = axial_feed_rate / lead
    load_ratio = total_thrust / buckling_limit * 100.0
    speed_ratio = operating_speed / critical_speed * 100.0

    if total_thrust > 0.5 * buckling_limit:
        status: Literal[
            "BALLSCREW_AXIAL_BUCKLING_RISK_WARNING",
            "BALLSCREW_CRITICAL_SPEED_WARNING",
            "BALLSCREW_MECHANICS_COMPLIANT",
        ] = "BALLSCREW_AXIAL_BUCKLING_RISK_WARNING"
    elif operating_speed > 0.8 * critical_speed:
        status = "BALLSCREW_CRITICAL_SPEED_WARNING"
    else:
        status = "BALLSCREW_MECHANICS_COMPLIANT"

    return BallscrewAxialMechanicsAuditPayload(
        source_guideway_load_audit=guideway,
        guide_friction_coefficient=friction,
        carriage_mass_kg=mass,
        carriage_acceleration_m_s2=acceleration,
        ballscrew_root_diameter_mm=root_diameter,
        ballscrew_lead_mm_per_rev=lead,
        ballscrew_length_mm=length,
        young_modulus_mpa=modulus,
        buckling_mounting_factor=buckling_factor,
        critical_speed_mounting_factor=speed_factor,
        axial_feed_rate_mm_per_min=axial_feed_rate,
        area_moment_of_inertia_mm4=inertia,
        total_axial_thrust_n=total_thrust,
        euler_buckling_limit_n=buckling_limit,
        critical_speed_rpm=critical_speed,
        operating_ballscrew_rpm=operating_speed,
        load_ratio_percent=load_ratio,
        speed_ratio_percent=speed_ratio,
        ballscrew_status=status,
    )


__all__ = ("BallscrewAuditError", "audit_ballscrew_mechanics")
