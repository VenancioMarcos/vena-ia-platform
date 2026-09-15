"""Analytical Palmgren spindle-bearing friction and thermal audit."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import ValidationError

from app.modules.cnc.schemas import (
    GuidewayLoadAuditPayload,
    SpindleBearingThermalAuditPayload,
)


class SpindleBearingAuditError(ValueError):
    """Raised when spindle-bearing thermal mechanics cannot be evaluated safely."""


def _finite(value: float, *, code: str) -> float:
    if isinstance(value, bool):
        raise SpindleBearingAuditError(code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SpindleBearingAuditError(code) from exc
    if not math.isfinite(number):
        raise SpindleBearingAuditError(code)
    return number


def _positive(value: float, *, code: str, upper: float) -> float:
    number = _finite(value, code=code)
    if not 0 < number <= upper:
        raise SpindleBearingAuditError(code)
    return number


def audit_spindle_bearing_thermal_load(
    source_guideway_load_audit: GuidewayLoadAuditPayload,
    *,
    internal_preload_n: float,
    load_friction_factor_f1: float,
    viscous_friction_factor_f0: float,
    bearing_mean_diameter_mm: float,
    lubricant_kinematic_viscosity_mm2_s: float,
    operating_rpm: float,
    convection_coefficient_w_m2_k: float,
    housing_dissipation_area_m2: float,
    max_admissible_temp_c: float,
) -> SpindleBearingThermalAuditPayload:
    """Resolve Palmgren friction torque, heat and steady bearing temperature."""

    try:
        guideway = GuidewayLoadAuditPayload.model_validate(source_guideway_load_audit)
    except ValidationError as exc:
        raise SpindleBearingAuditError("SPINDLE_BEARING_GUIDEWAY_SOURCE_INVALID") from exc

    preload = _positive(
        internal_preload_n,
        code="SPINDLE_BEARING_INTERNAL_PRELOAD_REQUIRED",
        upper=10_000_000.0,
    )
    load_factor = _positive(
        load_friction_factor_f1,
        code="SPINDLE_BEARING_LOAD_FACTOR_INVALID",
        upper=1.0,
    )
    viscous_factor = _positive(
        viscous_friction_factor_f0,
        code="SPINDLE_BEARING_VISCOUS_FACTOR_INVALID",
        upper=1_000.0,
    )
    mean_diameter = _positive(
        bearing_mean_diameter_mm,
        code="SPINDLE_BEARING_MEAN_DIAMETER_INVALID",
        upper=10_000.0,
    )
    viscosity = _positive(
        lubricant_kinematic_viscosity_mm2_s,
        code="SPINDLE_BEARING_VISCOSITY_INVALID",
        upper=100_000.0,
    )
    rpm = _positive(
        operating_rpm,
        code="SPINDLE_BEARING_OPERATING_RPM_INVALID",
        upper=100_000.0,
    )
    if rpm > guideway.source_power_force_audit.max_spindle_rpm:
        raise SpindleBearingAuditError("SPINDLE_BEARING_OPERATING_RPM_OUTSIDE_ENVELOPE")
    convection = _positive(
        convection_coefficient_w_m2_k,
        code="SPINDLE_BEARING_CONVECTION_INVALID",
        upper=1_000_000.0,
    )
    housing_area = _positive(
        housing_dissipation_area_m2,
        code="SPINDLE_BEARING_HOUSING_AREA_INVALID",
        upper=10_000.0,
    )
    maximum_temperature = _positive(
        max_admissible_temp_c,
        code="SPINDLE_BEARING_MAX_TEMPERATURE_INVALID",
        upper=500.0,
    )
    if maximum_temperature <= 20.0:
        raise SpindleBearingAuditError("SPINDLE_BEARING_MAX_TEMPERATURE_INVALID")

    combined_load = (
        math.sqrt(
            guideway.tangential_cutting_force_n**2
            + guideway.axial_feed_force_n**2
            + guideway.radial_cutting_force_n**2
        )
        + preload
    )
    load_torque = load_factor * combined_load * mean_diameter / 1_000.0
    viscosity_speed = viscosity * rpm
    if viscosity_speed >= 2_000.0:
        viscous_torque_n_mm = (
            1e-7 * viscous_factor * viscosity_speed ** (2.0 / 3.0) * mean_diameter**3
        )
    else:
        viscous_torque_n_mm = 160e-7 * viscous_factor * mean_diameter**3
    viscous_torque = viscous_torque_n_mm / 1_000.0
    total_torque = load_torque + viscous_torque
    heat = total_torque * (2.0 * math.pi * rpm / 60.0)
    temperature_rise = heat / (convection * housing_area)
    estimated_temperature = 20.0 + temperature_rise
    status: Literal[
        "SPINDLE_BEARING_OVERHEATING_WARNING",
        "SPINDLE_BEARING_THERMAL_COMPLIANT",
    ] = (
        "SPINDLE_BEARING_OVERHEATING_WARNING"
        if estimated_temperature > maximum_temperature
        else "SPINDLE_BEARING_THERMAL_COMPLIANT"
    )

    return SpindleBearingThermalAuditPayload(
        source_guideway_load_audit=guideway,
        internal_preload_n=preload,
        combined_equivalent_load_n=combined_load,
        load_friction_factor_f1=load_factor,
        viscous_friction_factor_f0=viscous_factor,
        bearing_mean_diameter_mm=mean_diameter,
        lubricant_kinematic_viscosity_mm2_s=viscosity,
        operating_rpm=rpm,
        convection_coefficient_w_m2_k=convection,
        housing_dissipation_area_m2=housing_area,
        max_admissible_temp_c=maximum_temperature,
        load_torque_nm=load_torque,
        viscous_torque_nm=viscous_torque,
        total_friction_torque_nm=total_torque,
        total_heat_dissipated_w=heat,
        steady_state_temperature_rise_c=temperature_rise,
        estimated_bearing_temp_c=estimated_temperature,
        bearing_status=status,
    )


__all__ = ("SpindleBearingAuditError", "audit_spindle_bearing_thermal_load")
