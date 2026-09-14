"""Analytical elastic-deflection audit for an unsupported turned workpiece."""

import math
from typing import Literal

from app.modules.cnc.schemas import PartElasticDeflectionAuditPayload


class PartDeflectionAuditError(ValueError):
    """Stable fail-closed reason for invalid analytical beam inputs."""


def material_young_modulus_mpa(material_profile: str) -> float:
    """Return the fixed analytical Young modulus for a supported material profile."""
    values = {
        "AISI_1020": 210_000.0,
        "ABNT_1045": 210_000.0,
        "ALUMINUM_6061_T6": 69_000.0,
    }
    try:
        return values[material_profile]
    except (KeyError, TypeError) as exc:
        raise PartDeflectionAuditError("PART_DEFLECTION_MATERIAL_PROFILE_INVALID") from exc


def audit_part_elastic_deflection(
    *,
    part_unsupported_length_mm: float,
    minimum_diameter_mm: float,
    radial_cutting_force_n: float,
    young_modulus_mpa: float,
    radial_tolerance_mm: float = 0.02,
) -> PartElasticDeflectionAuditPayload:
    """Model the part as a cylindrical cantilever with a radial point load."""
    values = (
        part_unsupported_length_mm,
        minimum_diameter_mm,
        radial_cutting_force_n,
        young_modulus_mpa,
        radial_tolerance_mm,
    )
    if (
        any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values)
        or any(not math.isfinite(value) or value <= 0 for value in values)
    ):
        raise PartDeflectionAuditError("PART_DEFLECTION_INPUT_INVALID")

    second_moment = math.pi * minimum_diameter_mm**4 / 64.0
    stiffness = 3.0 * young_modulus_mpa * second_moment / part_unsupported_length_mm**3
    deflection_um = radial_cutting_force_n / stiffness * 1_000.0
    if not all(math.isfinite(value) and value > 0 for value in (second_moment, stiffness, deflection_um)):
        raise PartDeflectionAuditError("PART_DEFLECTION_ESTIMATE_NON_CONVERGENT")
    status: Literal[
        "ELASTIC_DEFLECTION_COMPLIANT",
        "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING",
    ] = (
        "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING"
        if deflection_um > radial_tolerance_mm * 1_000.0
        else "ELASTIC_DEFLECTION_COMPLIANT"
    )
    return PartElasticDeflectionAuditPayload(
        part_unsupported_length_mm=float(part_unsupported_length_mm),
        minimum_diameter_mm=float(minimum_diameter_mm),
        radial_cutting_force_n=float(radial_cutting_force_n),
        young_modulus_mpa=float(young_modulus_mpa),
        second_moment_area_mm4=round(second_moment, 9),
        calculated_stiffness_n_per_mm=round(stiffness, 9),
        radial_tolerance_mm=float(radial_tolerance_mm),
        max_deflection_um=round(deflection_um, 9),
        deflection_status=status,
    )


__all__ = (
    "PartDeflectionAuditError",
    "audit_part_elastic_deflection",
    "material_young_modulus_mpa",
)
