"""Analytical cantilever rigidity and simplified chatter stability audit."""

from math import isfinite, pi
from typing import Literal

from app.modules.cnc.schemas import MachiningStabilityAuditPayload


def _positive(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    result = float(value)
    if not isfinite(result) or result <= 0:
        raise ValueError(code)
    return result


def audit_machining_stability(
    *,
    tool_id: str,
    tool_overhang_mm: float,
    tool_diameter_mm: float,
    young_modulus_mpa: float,
    cutting_force_n: float,
    specific_cutting_pressure_n_per_mm2: float,
    frf_real_compliance_mm_per_n: float,
    depth_of_cut_mm: float,
) -> MachiningStabilityAuditPayload:
    """Evaluate a cylindrical cantilever and a conservative analytical chatter limit."""
    if not isinstance(tool_id, str) or not tool_id.strip():
        raise ValueError("STABILITY_TOOL_ID_INVALID")
    overhang = _positive(tool_overhang_mm, code="STABILITY_TOOL_OVERHANG_INVALID")
    diameter = _positive(tool_diameter_mm, code="STABILITY_TOOL_DIAMETER_INVALID")
    modulus = _positive(young_modulus_mpa, code="STABILITY_YOUNG_MODULUS_INVALID")
    force = _positive(cutting_force_n, code="STABILITY_CUTTING_FORCE_INVALID")
    pressure = _positive(
        specific_cutting_pressure_n_per_mm2,
        code="STABILITY_SPECIFIC_CUTTING_PRESSURE_INVALID",
    )
    compliance = _positive(
        frf_real_compliance_mm_per_n,
        code="STABILITY_FRF_COMPLIANCE_INVALID",
    )
    depth = _positive(depth_of_cut_mm, code="STABILITY_DEPTH_OF_CUT_INVALID")

    ratio = overhang / diameter
    inertia = pi * diameter**4 / 64
    stiffness = 3 * modulus * inertia / overhang**3
    deflection_um = force / stiffness * 1_000
    stability_limit = 1 / (2 * pressure * compliance)
    status: Literal["DYNAMICALLY_STABLE", "CHATTER_HIGH_RISK_WARNING"] = (
        "DYNAMICALLY_STABLE"
        if ratio <= 4 and depth <= stability_limit
        else "CHATTER_HIGH_RISK_WARNING"
    )
    return MachiningStabilityAuditPayload(
        tool_id=tool_id.strip(),
        tool_overhang_mm=overhang,
        tool_diameter_mm=diameter,
        overhang_ratio_l_d=round(ratio, 9),
        young_modulus_mpa=modulus,
        second_moment_area_mm4=round(inertia, 9),
        equivalent_stiffness_n_per_mm=round(stiffness, 9),
        cutting_force_n=force,
        static_deflection_um=round(deflection_um, 9),
        specific_cutting_pressure_n_per_mm2=pressure,
        frf_real_compliance_mm_per_n=compliance,
        depth_of_cut_mm=depth,
        stability_limit_depth_mm=round(stability_limit, 9),
        stability_status=status,
    )


__all__ = ("audit_machining_stability",)
