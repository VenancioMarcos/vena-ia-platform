"""Build deterministic analytical coolant demand audits for review-only reports."""

from typing import Literal

from app.modules.cnc.schemas import (
    CoolantPressureFlowAuditPayload,
    CoolantZoneRequirement,
)


_COOLANT_REQUIREMENTS: dict[
    str,
    tuple[tuple[str, float, float], ...],
] = {
    "FLOOD": (
        ("PRIMARY_SHEAR_ZONE", 12.0, 4.0),
        ("SECONDARY_TOOL_CHIP_INTERFACE", 15.0, 6.0),
        ("TERTIARY_TOOL_WORKPIECE_INTERFACE", 10.0, 3.0),
    ),
    "MQL": (
        ("PRIMARY_SHEAR_ZONE", 0.05, 5.0),
        ("SECONDARY_TOOL_CHIP_INTERFACE", 0.08, 6.0),
        ("TERTIARY_TOOL_WORKPIECE_INTERFACE", 0.04, 4.0),
    ),
}


def audit_coolant_pressure_flow(
    *,
    coolant_mode: Literal["FLOOD", "MQL"],
    programmed_flow_l_per_min: float,
    programmed_pressure_bar: float,
) -> CoolantPressureFlowAuditPayload:
    """Compare declared analytical supply against immutable requirements per cutting zone."""
    requirements = tuple(
        CoolantZoneRequirement(
            cutting_zone=zone,  # type: ignore[arg-type]
            minimum_flow_l_per_min=minimum_flow,
            minimum_pressure_bar=minimum_pressure,
        )
        for zone, minimum_flow, minimum_pressure in _COOLANT_REQUIREMENTS[coolant_mode]
    )
    minimum_flow = max(item.minimum_flow_l_per_min for item in requirements)
    minimum_pressure = max(item.minimum_pressure_bar for item in requirements)
    within_requirements = (
        programmed_flow_l_per_min >= minimum_flow
        and programmed_pressure_bar >= minimum_pressure
    )
    return CoolantPressureFlowAuditPayload(
        coolant_mode=coolant_mode,
        programmed_flow_l_per_min=programmed_flow_l_per_min,
        programmed_pressure_bar=programmed_pressure_bar,
        zone_requirements=requirements,
        minimum_required_flow_l_per_min=minimum_flow,
        minimum_required_pressure_bar=minimum_pressure,
        flow_margin_percent=(programmed_flow_l_per_min - minimum_flow)
        / minimum_flow
        * 100.0,
        pressure_margin_percent=(programmed_pressure_bar - minimum_pressure)
        / minimum_pressure
        * 100.0,
        thermal_dissipation_status=(
            "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS"
            if within_requirements
            else "INSUFFICIENT_THERMAL_DISSIPATION_WARNING"
        ),
    )


__all__ = ("audit_coolant_pressure_flow",)
