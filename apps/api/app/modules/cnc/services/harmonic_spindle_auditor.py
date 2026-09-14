"""Analytical spindle resonance and residual-unbalance audit."""

import math
from typing import Literal

from app.modules.cnc.schemas import SpindleHarmonicDynamicsAuditPayload


class HarmonicSpindleAuditError(ValueError):
    """Stable fail-closed reason for invalid analytical rotor inputs."""


def _finite(value: float, *, code: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise HarmonicSpindleAuditError(code)
    return float(value)


def material_density_kg_m3(material_profile: str) -> float:
    """Return the fixed analytical density for a supported material profile."""
    values = {
        "AISI_1020": 7_850.0,
        "ABNT_1045": 7_850.0,
        "ALUMINUM_6061_T6": 2_700.0,
    }
    try:
        return values[material_profile]
    except (KeyError, TypeError) as exc:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_MATERIAL_PROFILE_INVALID") from exc


def cylindrical_workpiece_mass_kg(
    *, diameter_mm: float, length_mm: float, density_kg_m3: float
) -> float:
    """Calculate a conservative cylindrical analytical workpiece mass."""
    diameter = _finite(diameter_mm, code="SPINDLE_HARMONIC_DIAMETER_INVALID")
    length = _finite(length_mm, code="SPINDLE_HARMONIC_LENGTH_INVALID")
    density = _finite(density_kg_m3, code="SPINDLE_HARMONIC_DENSITY_INVALID")
    if not 0 < diameter <= 10_000:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_DIAMETER_INVALID")
    if not 0 < length <= 100_000:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_LENGTH_INVALID")
    if not 0 < density <= 100_000:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_DENSITY_INVALID")
    radius_m = diameter / 2_000.0
    mass = density * math.pi * radius_m**2 * (length / 1_000.0)
    if not math.isfinite(mass) or mass <= 0:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_MASS_NON_CONVERGENT")
    return mass


def audit_spindle_harmonic_dynamics(
    *,
    system_stiffness_n_per_m: float,
    effective_mass_kg: float,
    workpiece_mass_kg: float,
    mass_eccentricity_mm: float,
    operating_rpm: float,
    bearing_admissible_force_n: float,
    resonance_exclusion_percent: float = 15.0,
) -> SpindleHarmonicDynamicsAuditPayload:
    """Estimate the first critical speed and residual 1x unbalance force."""
    stiffness = _finite(
        system_stiffness_n_per_m,
        code="SPINDLE_HARMONIC_STIFFNESS_INVALID",
    )
    effective_mass = _finite(
        effective_mass_kg,
        code="SPINDLE_HARMONIC_EFFECTIVE_MASS_INVALID",
    )
    workpiece_mass = _finite(
        workpiece_mass_kg,
        code="SPINDLE_HARMONIC_WORKPIECE_MASS_INVALID",
    )
    eccentricity = _finite(
        mass_eccentricity_mm,
        code="SPINDLE_HARMONIC_ECCENTRICITY_INVALID",
    )
    rpm = _finite(operating_rpm, code="SPINDLE_HARMONIC_OPERATING_RPM_INVALID")
    bearing_limit = _finite(
        bearing_admissible_force_n,
        code="SPINDLE_HARMONIC_BEARING_FORCE_LIMIT_INVALID",
    )
    exclusion = _finite(
        resonance_exclusion_percent,
        code="SPINDLE_HARMONIC_EXCLUSION_PERCENT_INVALID",
    )

    if not 0 < stiffness <= 1e21:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_STIFFNESS_INVALID")
    if not 0 < effective_mass <= 1e6:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_EFFECTIVE_MASS_INVALID")
    if not 0 < workpiece_mass <= 1e6:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_WORKPIECE_MASS_INVALID")
    if effective_mass > workpiece_mass:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_EFFECTIVE_MASS_INVALID")
    if not 0 <= eccentricity <= 100:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_ECCENTRICITY_INVALID")
    if not 0 < rpm <= 100_000:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_OPERATING_RPM_INVALID")
    if not 0 < bearing_limit <= 100_000_000:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_BEARING_FORCE_LIMIT_INVALID")
    if not 0 < exclusion < 100:
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_EXCLUSION_PERCENT_INVALID")

    natural_angular_frequency_rad_s = math.sqrt(stiffness / effective_mass)
    first_critical_rpm = natural_angular_frequency_rad_s * 60.0 / (2.0 * math.pi)
    operating_angular_velocity_rad_s = 2.0 * math.pi * rpm / 60.0
    proximity_percent = abs(rpm - first_critical_rpm) / first_critical_rpm * 100.0
    unbalance_force_n = (
        workpiece_mass * (eccentricity / 1_000.0) * operating_angular_velocity_rad_s**2
    )
    results = (
        natural_angular_frequency_rad_s,
        first_critical_rpm,
        operating_angular_velocity_rad_s,
        proximity_percent,
        unbalance_force_n,
    )
    if any(not math.isfinite(value) or value < 0 for value in results):
        raise HarmonicSpindleAuditError("SPINDLE_HARMONIC_ESTIMATE_NON_CONVERGENT")

    status: Literal[
        "SPINDLE_DYNAMICS_COMPLIANT",
        "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING",
        "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING",
    ]
    if proximity_percent <= exclusion:
        status = "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING"
    elif unbalance_force_n > bearing_limit:
        status = "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING"
    else:
        status = "SPINDLE_DYNAMICS_COMPLIANT"

    return SpindleHarmonicDynamicsAuditPayload(
        system_stiffness_n_per_m=stiffness,
        effective_mass_kg=effective_mass,
        workpiece_mass_kg=workpiece_mass,
        mass_eccentricity_mm=eccentricity,
        natural_angular_frequency_rad_s=natural_angular_frequency_rad_s,
        first_critical_rpm=first_critical_rpm,
        operating_rpm=rpm,
        resonance_proximity_percent=proximity_percent,
        resonance_exclusion_percent=exclusion,
        unbalance_force_n=unbalance_force_n,
        bearing_admissible_force_n=bearing_limit,
        dynamic_status=status,
    )


__all__ = (
    "HarmonicSpindleAuditError",
    "audit_spindle_harmonic_dynamics",
    "cylindrical_workpiece_mass_kg",
    "material_density_kg_m3",
)
