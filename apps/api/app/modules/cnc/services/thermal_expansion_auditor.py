"""Analytical thermal expansion and axis-drift audit for review-only reports."""

import math
from typing import Literal

from app.modules.cnc.schemas import ThermalExpansionDriftAuditPayload


MaterialProfile = Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
_MATERIAL_ALPHA: dict[MaterialProfile, float] = {
    "AISI_1020": 12.0e-6,
    "ABNT_1045": 12.0e-6,
    "ALUMINUM_6061_T6": 23.0e-6,
}


def _material(reference: str) -> MaterialProfile:
    normalized = reference.upper().replace("Í", "I").replace("Ç", "C")
    if "6061" in normalized:
        return "ALUMINUM_6061_T6"
    if "1045" in normalized:
        return "ABNT_1045"
    if "1020" in normalized:
        return "AISI_1020"
    raise ValueError("THERMAL_MATERIAL_UNSUPPORTED")


def _finite(value: float, *, minimum: float, maximum: float, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(code)
    result = float(value)
    if result < minimum or result > maximum:
        raise ValueError(code)
    return result


def audit_thermal_expansion_drift(
    material_reference: str,
    *,
    workpiece_mean_temperature_c: float,
    spindle_mean_temperature_c: float,
    workpiece_length_mm: float,
    workpiece_diameter_mm: float,
    spindle_effective_length_mm: float,
    z_axis_tolerance_um: float,
    x_axis_tolerance_um: float,
) -> ThermalExpansionDriftAuditPayload:
    material = _material(material_reference)
    workpiece_temperature = _finite(
        workpiece_mean_temperature_c, minimum=-40, maximum=300, code="THERMAL_WORKPIECE_TEMPERATURE_INVALID"
    )
    spindle_temperature = _finite(
        spindle_mean_temperature_c, minimum=-40, maximum=300, code="THERMAL_SPINDLE_TEMPERATURE_INVALID"
    )
    if workpiece_temperature < 20 or spindle_temperature < 20:
        raise ValueError("THERMAL_DELTA_TEMPERATURE_INCONSISTENT")
    length = _finite(workpiece_length_mm, minimum=1e-12, maximum=100_000, code="THERMAL_WORKPIECE_LENGTH_INVALID")
    diameter = _finite(workpiece_diameter_mm, minimum=1e-12, maximum=100_000, code="THERMAL_WORKPIECE_DIAMETER_INVALID")
    spindle_length = _finite(spindle_effective_length_mm, minimum=1e-12, maximum=100_000, code="THERMAL_SPINDLE_LENGTH_INVALID")
    z_tolerance = _finite(z_axis_tolerance_um, minimum=1e-12, maximum=1_000_000, code="THERMAL_Z_TOLERANCE_INVALID")
    x_tolerance = _finite(x_axis_tolerance_um, minimum=1e-12, maximum=1_000_000, code="THERMAL_X_TOLERANCE_INVALID")
    alpha = _MATERIAL_ALPHA[material]
    spindle_alpha = 12.0e-6
    workpiece_delta = workpiece_temperature - 20.0
    spindle_delta = spindle_temperature - 20.0
    workpiece_z = alpha * length * workpiece_delta * 1_000
    workpiece_x = alpha * (diameter / 2.0) * workpiece_delta * 1_000
    spindle_z = spindle_alpha * spindle_length * spindle_delta * 1_000
    total_z = workpiece_z + spindle_z
    total_x = workpiece_x
    status: Literal[
        "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE",
        "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING",
    ] = (
        "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING"
        if total_z > z_tolerance or total_x > x_tolerance
        else "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE"
    )
    return ThermalExpansionDriftAuditPayload(
        material_profile=material,
        linear_expansion_coefficient_per_c=alpha,
        spindle_expansion_coefficient_per_c=spindle_alpha,
        workpiece_mean_temperature_c=workpiece_temperature,
        spindle_mean_temperature_c=spindle_temperature,
        workpiece_mean_temperature_rise_c=workpiece_delta,
        spindle_mean_temperature_rise_c=spindle_delta,
        workpiece_axial_reference_length_mm=length,
        workpiece_diameter_reference_mm=diameter,
        spindle_z_reference_length_mm=spindle_length,
        workpiece_z_expansion_um=workpiece_z,
        workpiece_x_expansion_um=workpiece_x,
        spindle_z_drift_um=spindle_z,
        total_z_axis_drift_um=total_z,
        total_x_axis_drift_um=total_x,
        z_axis_tolerance_um=z_tolerance,
        x_axis_tolerance_um=x_tolerance,
        audit_status=status,
    )


__all__ = ("audit_thermal_expansion_drift",)
