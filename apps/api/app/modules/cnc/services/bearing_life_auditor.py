"""Deterministic ISO 281 spindle-bearing fatigue-life audit."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import ValidationError

from app.modules.cnc.schemas import (
    SpindleBearingLifeAuditPayload,
    SpindleBearingThermalAuditPayload,
)


class BearingLifeAuditError(ValueError):
    """Raised when bearing fatigue life cannot be evaluated safely."""


def _positive(value: float, *, code: str, upper: float) -> float:
    if isinstance(value, bool):
        raise BearingLifeAuditError(code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BearingLifeAuditError(code) from exc
    if not math.isfinite(number) or not 0 < number <= upper:
        raise BearingLifeAuditError(code)
    return number


def iso_viscosity_modification_factor(viscosity_ratio_kappa: float) -> float:
    """Return the declared conservative kappa-only ISO modification schedule."""

    kappa = _positive(
        viscosity_ratio_kappa,
        code="BEARING_LIFE_VISCOSITY_RATIO_INVALID",
        upper=1_000_000.0,
    )
    if kappa < 0.4:
        return 0.2
    if kappa < 1.0:
        return 0.5
    if kappa < 2.0:
        return 1.0
    return 1.2


def audit_spindle_bearing_l10h_life(
    source_spindle_bearing_thermal_audit: SpindleBearingThermalAuditPayload,
    *,
    bearing_type: Literal[
        "ANGULAR_CONTACT_BALL",
        "CYLINDRICAL_ROLLER",
        "TAPERED_ROLLER",
    ],
    axial_preload_n: float,
    radial_load_factor_x: float,
    axial_load_factor_y: float,
    dynamic_capacity_c_n: float,
    required_kinematic_viscosity_nu1_mm2_s: float,
    minimum_admissible_l10h_hours: float,
) -> SpindleBearingLifeAuditPayload:
    """Calculate temperature-adjusted ISO 281 L10 and L10h bearing life."""

    try:
        thermal = SpindleBearingThermalAuditPayload.model_validate(
            source_spindle_bearing_thermal_audit
        )
    except ValidationError as exc:
        raise BearingLifeAuditError("BEARING_LIFE_THERMAL_SOURCE_INVALID") from exc

    if bearing_type == "ANGULAR_CONTACT_BALL":
        life_exponent = 3.0
    elif bearing_type in {"CYLINDRICAL_ROLLER", "TAPERED_ROLLER"}:
        life_exponent = 10.0 / 3.0
    else:
        raise BearingLifeAuditError("BEARING_LIFE_TYPE_UNSUPPORTED")

    preload = _positive(
        axial_preload_n,
        code="BEARING_LIFE_AXIAL_PRELOAD_INVALID",
        upper=10_000_000.0,
    )
    radial_factor = _positive(
        radial_load_factor_x,
        code="BEARING_LIFE_RADIAL_FACTOR_INVALID",
        upper=10.0,
    )
    axial_factor = _positive(
        axial_load_factor_y,
        code="BEARING_LIFE_AXIAL_FACTOR_INVALID",
        upper=10.0,
    )
    capacity = _positive(
        dynamic_capacity_c_n,
        code="BEARING_LIFE_DYNAMIC_CAPACITY_REQUIRED",
        upper=1_000_000_000.0,
    )
    required_viscosity = _positive(
        required_kinematic_viscosity_nu1_mm2_s,
        code="BEARING_LIFE_REQUIRED_VISCOSITY_INVALID",
        upper=100_000.0,
    )
    minimum_life = _positive(
        minimum_admissible_l10h_hours,
        code="BEARING_LIFE_MINIMUM_L10H_INVALID",
        upper=1_000_000_000.0,
    )
    rpm = _positive(
        thermal.operating_rpm,
        code="BEARING_LIFE_OPERATING_RPM_INVALID",
        upper=100_000.0,
    )

    guideway = thermal.source_guideway_load_audit
    radial_load = _positive(
        guideway.radial_cutting_force_n,
        code="BEARING_LIFE_RADIAL_LOAD_INVALID",
        upper=1_000_000_000.0,
    )
    axial_load = _positive(
        guideway.axial_feed_force_n + preload,
        code="BEARING_LIFE_AXIAL_LOAD_INVALID",
        upper=1_000_000_000.0,
    )
    equivalent_load = radial_factor * radial_load + axial_factor * axial_load
    equivalent_load = _positive(
        equivalent_load,
        code="BEARING_LIFE_EQUIVALENT_LOAD_INVALID",
        upper=1_000_000_000.0,
    )

    temperature_delta = thermal.estimated_bearing_temp_c - thermal.ambient_temperature_c
    operating_viscosity = thermal.lubricant_kinematic_viscosity_mm2_s * math.exp(
        -0.025 * temperature_delta
    )
    operating_viscosity = _positive(
        operating_viscosity,
        code="BEARING_LIFE_OPERATING_VISCOSITY_INVALID",
        upper=100_000.0,
    )
    kappa = operating_viscosity / required_viscosity
    a_iso = iso_viscosity_modification_factor(kappa)
    basic_l10 = (capacity / equivalent_load) ** life_exponent
    l10 = a_iso * basic_l10
    l10h = 1_000_000.0 * l10 / (60.0 * rpm)
    status: Literal[
        "PREMATURE_BEARING_FATIGUE_WARNING",
        "BEARING_FATIGUE_LIFE_COMPLIANT",
    ] = (
        "PREMATURE_BEARING_FATIGUE_WARNING"
        if l10h < minimum_life
        else "BEARING_FATIGUE_LIFE_COMPLIANT"
    )

    return SpindleBearingLifeAuditPayload(
        source_spindle_bearing_thermal_audit=thermal,
        bearing_type=bearing_type,
        life_exponent_p=life_exponent,
        axial_preload_n=preload,
        radial_load_n=radial_load,
        axial_load_n=axial_load,
        radial_load_factor_x=radial_factor,
        axial_load_factor_y=axial_factor,
        equivalent_dynamic_load_n=equivalent_load,
        dynamic_capacity_c_n=capacity,
        required_kinematic_viscosity_nu1_mm2_s=required_viscosity,
        operating_kinematic_viscosity_nu_mm2_s=operating_viscosity,
        viscosity_ratio_kappa=kappa,
        a_iso_modification_factor=a_iso,
        basic_l10_million_revs=basic_l10,
        l10_million_revs=l10,
        operating_rpm=rpm,
        l10h_hours=l10h,
        minimum_admissible_l10h_hours=minimum_life,
        bearing_life_status=status,
    )


__all__ = (
    "BearingLifeAuditError",
    "audit_spindle_bearing_l10h_life",
    "iso_viscosity_modification_factor",
)
