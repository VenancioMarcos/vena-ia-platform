"""Deterministic chip-formation and breaking audit for analytical review only."""

from dataclasses import dataclass
import math
from typing import Literal

from app.modules.cnc.schemas import (
    ChipBreakerSafeEnvelope,
    ChipBreakingMachinabilityAuditPayload,
)


MaterialProfile = Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
ChipBreakerFamily = Literal["PM", "PR", "PF"]


@dataclass(frozen=True)
class _MaterialChipParameters:
    profile: MaterialProfile
    compression_ratio_at_six_degree_rake: float


_MATERIALS = {
    "AISI_1020": _MaterialChipParameters("AISI_1020", 2.2),
    "ABNT_1045": _MaterialChipParameters("ABNT_1045", 2.4),
    "ALUMINUM_6061_T6": _MaterialChipParameters("ALUMINUM_6061_T6", 1.8),
}

_SAFE_ENVELOPES = (
    ChipBreakerSafeEnvelope(
        chipbreaker_reference="CNMG_120408_PM_TABULATED",
        feed_min_mm_per_rev=0.15,
        feed_max_mm_per_rev=0.40,
        depth_of_cut_min_mm=1.0,
        depth_of_cut_max_mm=4.0,
    ),
    ChipBreakerSafeEnvelope(
        chipbreaker_reference="CNMG_120408_PR_TABULATED",
        feed_min_mm_per_rev=0.25,
        feed_max_mm_per_rev=0.60,
        depth_of_cut_min_mm=2.0,
        depth_of_cut_max_mm=6.0,
    ),
    ChipBreakerSafeEnvelope(
        chipbreaker_reference="CNMG_120408_PF_TABULATED",
        feed_min_mm_per_rev=0.05,
        feed_max_mm_per_rev=0.20,
        depth_of_cut_min_mm=0.2,
        depth_of_cut_max_mm=2.0,
    ),
)
_FAMILY_BY_REFERENCE: dict[str, ChipBreakerFamily] = {
    "CNMG_120408_PM_TABULATED": "PM",
    "CNMG_120408_PR_TABULATED": "PR",
    "CNMG_120408_PF_TABULATED": "PF",
}


def _material(reference: str) -> _MaterialChipParameters:
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("CHIP_BREAKING_MATERIAL_REFERENCE_INVALID")
    normalized = reference.upper().replace("Í", "I").replace("Ç", "C")
    if "6061" in normalized:
        return _MATERIALS["ALUMINUM_6061_T6"]
    if "1045" in normalized:
        return _MATERIALS["ABNT_1045"]
    if "1020" in normalized:
        return _MATERIALS["AISI_1020"]
    raise ValueError("CHIP_BREAKING_MATERIAL_UNSUPPORTED")


def _finite(
    value: float,
    *,
    minimum: float,
    maximum: float,
    code: str,
) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(code)
    result = float(value)
    if result < minimum or result > maximum:
        raise ValueError(code)
    return result


def audit_chip_breaking_machinability(
    material_reference: str,
    *,
    chipbreaker_reference: str,
    feed_mm_per_rev: float,
    depth_of_cut_mm: float,
    insert_nose_radius_mm: float,
    cutting_edge_angle_deg: float,
    rake_angle_deg: float,
) -> ChipBreakingMachinabilityAuditPayload:
    """Calculate chip geometry and compare the operating point to a declared table."""
    material = _material(material_reference)
    if not isinstance(chipbreaker_reference, str) or not chipbreaker_reference.strip():
        raise ValueError("CHIP_BREAKER_REFERENCE_INVALID")
    selected = tuple(
        item
        for item in _SAFE_ENVELOPES
        if item.chipbreaker_reference == chipbreaker_reference.strip()
    )
    if len(selected) != 1:
        raise ValueError("CHIP_BREAKER_GEOMETRY_UNSUPPORTED")
    envelope = selected[0]
    family = _FAMILY_BY_REFERENCE[envelope.chipbreaker_reference]

    feed = _finite(
        feed_mm_per_rev,
        minimum=1e-12,
        maximum=10.0,
        code="CHIP_BREAKING_FEED_INVALID",
    )
    depth = _finite(
        depth_of_cut_mm,
        minimum=1e-12,
        maximum=100.0,
        code="CHIP_BREAKING_DEPTH_INVALID",
    )
    nose_radius = _finite(
        insert_nose_radius_mm,
        minimum=1e-12,
        maximum=20.0,
        code="CHIP_BREAKING_NOSE_RADIUS_INVALID",
    )
    cutting_edge_angle = _finite(
        cutting_edge_angle_deg,
        minimum=1e-12,
        maximum=179.999999999,
        code="CHIP_BREAKING_CUTTING_EDGE_ANGLE_INVALID",
    )
    rake_angle = _finite(
        rake_angle_deg,
        minimum=-20.0,
        maximum=40.0,
        code="CHIP_BREAKING_RAKE_ANGLE_INVALID",
    )
    sin_kr = math.sin(math.radians(cutting_edge_angle))
    if not math.isfinite(sin_kr) or sin_kr <= 0:
        raise ValueError("CHIP_BREAKING_CUTTING_EDGE_ANGLE_INVALID")

    uncut_thickness = feed * sin_kr
    chip_width = depth / sin_kr
    compression_ratio = max(
        1.0,
        material.compression_ratio_at_six_degree_rake - 0.02 * (rake_angle - 6.0),
    )
    formed_thickness = uncut_thickness * compression_ratio
    free_chip_length = 2.0 * math.pi * (nose_radius + formed_thickness)
    values = (
        uncut_thickness,
        chip_width,
        compression_ratio,
        formed_thickness,
        free_chip_length,
    )
    if not all(math.isfinite(value) and value > 0 for value in values):
        raise ValueError("CHIP_BREAKING_ESTIMATE_NON_CONVERGENT")
    inside = (
        envelope.feed_min_mm_per_rev <= feed <= envelope.feed_max_mm_per_rev
        and envelope.depth_of_cut_min_mm <= depth <= envelope.depth_of_cut_max_mm
    )

    return ChipBreakingMachinabilityAuditPayload(
        material_profile=material.profile,
        chipbreaker_family=family,
        chipbreaker_reference=envelope.chipbreaker_reference,
        feed_mm_per_rev=feed,
        depth_of_cut_mm=depth,
        insert_nose_radius_mm=nose_radius,
        cutting_edge_angle_deg=cutting_edge_angle,
        rake_angle_deg=rake_angle,
        uncut_chip_thickness_mm=round(uncut_thickness, 9),
        chip_width_mm=round(chip_width, 9),
        formed_chip_thickness_mm=round(formed_thickness, 9),
        chip_compression_ratio=round(compression_ratio, 9),
        free_chip_length_mm=round(free_chip_length, 9),
        safe_breaking_envelopes=_SAFE_ENVELOPES,
        audit_status=(
            "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
            if inside
            else "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
        ),
    )


__all__ = ("audit_chip_breaking_machinability",)
