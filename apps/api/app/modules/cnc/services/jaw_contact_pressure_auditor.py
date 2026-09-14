"""Analytical three-jaw contact-pressure and surface-indentation audit."""

import math
from typing import Literal, cast

from app.modules.cnc.schemas import (
    JawClampingPressureAuditPayload,
    WorkholdingClampingAuditPayload,
)


class JawContactPressureAuditError(ValueError):
    """Stable fail-closed reason for invalid analytical jaw-contact inputs."""


MaterialProfile = Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]


def _finite(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise JawContactPressureAuditError(code)
    return float(value)


def material_yield_strength_mpa(material_profile: str) -> float:
    """Return the fixed analytical yield strength for a supported material."""
    values = {
        "AISI_1020": 250.0,
        "ABNT_1045": 350.0,
        "ALUMINUM_6061_T6": 276.0,
    }
    try:
        return values[material_profile]
    except (KeyError, TypeError) as exc:
        raise JawContactPressureAuditError("JAW_CONTACT_MATERIAL_PROFILE_INVALID") from exc


def audit_jaw_contact_pressure(
    workholding_audit: WorkholdingClampingAuditPayload,
    *,
    material_profile: str,
    jaw_width_mm: float,
    effective_contact_length_mm: float,
) -> JawClampingPressureAuditPayload:
    """Estimate mean pressure for three jaws from Route 27 residual force."""
    try:
        workholding = WorkholdingClampingAuditPayload.model_validate(workholding_audit)
    except (TypeError, ValueError) as exc:
        raise JawContactPressureAuditError("JAW_CONTACT_WORKHOLDING_AUDIT_INVALID") from exc
    width = _finite(jaw_width_mm, code="JAW_CONTACT_WIDTH_INVALID")
    contact_length = _finite(
        effective_contact_length_mm,
        code="JAW_CONTACT_EFFECTIVE_LENGTH_INVALID",
    )
    if not 0 < width <= 10_000:
        raise JawContactPressureAuditError("JAW_CONTACT_WIDTH_INVALID")
    if not 0 < contact_length <= 100_000:
        raise JawContactPressureAuditError("JAW_CONTACT_EFFECTIVE_LENGTH_INVALID")
    dynamic_force = _finite(
        workholding.dynamic_clamping_force_total_n,
        code="JAW_CONTACT_DYNAMIC_FORCE_INVALID",
    )
    if dynamic_force <= 0:
        raise JawContactPressureAuditError("JAW_CONTACT_DYNAMIC_FORCE_INVALID")

    yield_strength = material_yield_strength_mpa(material_profile)
    validated_material = cast(MaterialProfile, material_profile)
    contact_area = width * contact_length
    dynamic_force_per_jaw = dynamic_force / 3.0
    mean_pressure = dynamic_force_per_jaw / contact_area
    required_total_force = (
        workholding.required_safety_factor
        * workholding.axial_cutting_force_n
        / workholding.friction_coefficient
    )
    minimum_retention_pressure = required_total_force / (3.0 * contact_area)
    pressure_ratio_percent = mean_pressure / yield_strength * 100.0
    results = (
        contact_area,
        dynamic_force_per_jaw,
        mean_pressure,
        minimum_retention_pressure,
        pressure_ratio_percent,
    )
    if any(not math.isfinite(value) or value <= 0 for value in results):
        raise JawContactPressureAuditError("JAW_CONTACT_ESTIMATE_NON_CONVERGENT")

    status: Literal[
        "JAW_SURFACE_INDENTATION_RISK_WARNING",
        "INSUFFICIENT_CLAMPING_PRESSURE_WARNING",
        "CLAMPING_PRESSURE_COMPLIANT",
    ]
    if mean_pressure > 0.6 * yield_strength:
        status = "JAW_SURFACE_INDENTATION_RISK_WARNING"
    elif mean_pressure < minimum_retention_pressure:
        status = "INSUFFICIENT_CLAMPING_PRESSURE_WARNING"
    else:
        status = "CLAMPING_PRESSURE_COMPLIANT"

    return JawClampingPressureAuditPayload(
        source_workholding_clamping_audit=workholding,
        material_profile=validated_material,
        jaw_width_mm=width,
        effective_contact_length_mm=contact_length,
        contact_area_mm2=contact_area,
        dynamic_force_per_jaw_n=dynamic_force_per_jaw,
        minimum_retention_pressure_mpa=minimum_retention_pressure,
        mean_contact_pressure_mpa=mean_pressure,
        material_yield_strength_mpa=yield_strength,
        pressure_ratio_percent=pressure_ratio_percent,
        clamping_pressure_status=status,
    )


__all__ = (
    "JawContactPressureAuditError",
    "audit_jaw_contact_pressure",
    "material_yield_strength_mpa",
)
