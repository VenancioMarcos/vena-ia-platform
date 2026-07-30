import math
from dataclasses import dataclass

from app.modules.manufacturing.schemas import (
    MaterialFamily,
    MillingInput,
    MillingRecommendation,
)


@dataclass(frozen=True)
class CuttingRule:
    cutting_speed_m_min: float
    feed_per_tooth_mm: float


class MillingRecommendationService:
    """Deterministic preliminary rules; output always requires engineering review."""

    _rules = {
        MaterialFamily.ALUMINUM: CuttingRule(300.0, 0.10),
        MaterialFamily.CARBON_STEEL: CuttingRule(120.0, 0.05),
        MaterialFamily.STAINLESS_STEEL: CuttingRule(70.0, 0.035),
    }

    def recommend(self, request: MillingInput) -> MillingRecommendation:
        rule = self._rules[request.material]
        theoretical_rpm = (
            1000.0 * rule.cutting_speed_m_min
        ) / (math.pi * request.tool_diameter_mm)
        rpm = min(theoretical_rpm, request.machine_max_rpm)
        theoretical_feed = rpm * request.tool_teeth * rule.feed_per_tooth_mm
        feed = min(theoretical_feed, request.machine_max_feed_mm_min)
        factors: list[str] = []
        if rpm < theoretical_rpm:
            factors.append("MACHINE_MAX_RPM")
        if feed < theoretical_feed:
            factors.append("MACHINE_MAX_FEED")
        return MillingRecommendation(
            operation="MILLING_PRELIMINARY",
            material=request.material,
            cutting_speed_m_min=rule.cutting_speed_m_min,
            feed_per_tooth_mm=rule.feed_per_tooth_mm,
            spindle_rpm=round(rpm, 2),
            feed_mm_min=round(feed, 2),
            estimated_cutting_time_min=round(request.cutting_length_mm / feed, 3),
            limiting_factors=factors,
            status="PRELIMINARY_REQUIRES_HUMAN_REVIEW",
            calculation_basis=[
                "rpm = 1000 × cutting_speed / (pi × tool_diameter)",
                "feed = rpm × tool_teeth × feed_per_tooth",
                "cutting_time = cutting_length / feed",
            ],
            warnings=[
                "Internal preliminary defaults; not universal cutting data.",
                "Validate exact material grade, hardness, tool geometry/coating and manufacturer data.",
                "Validate axial/radial depth, coolant, workholding, machine rigidity and tool overhang.",
                "Human engineering review is mandatory before any real process.",
            ],
        )
