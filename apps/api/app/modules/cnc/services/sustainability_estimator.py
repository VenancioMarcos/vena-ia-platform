"""Analytical electrical-energy and carbon-footprint estimates for CNC reports."""

from math import isfinite
from typing import Literal

from app.modules.cnc.schemas import MachiningSustainabilityAuditPayload


GridRegion = Literal["BRASIL_SIN", "USA_AVG", "EU_AVG"]
_GRID_FACTORS: dict[GridRegion, float] = {
    "BRASIL_SIN": 0.085,
    "USA_AVG": 0.385,
    "EU_AVG": 0.230,
}


def _positive(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    result = float(value)
    if not isfinite(result) or result <= 0:
        raise ValueError(code)
    return result


def _nonnegative(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    result = float(value)
    if not isfinite(result) or result < 0:
        raise ValueError(code)
    return result


def estimate_sustainability(
    *,
    motor_power_kw: float,
    cutting_time_minutes: float,
    total_cycle_time_minutes: float,
    standby_power_kw: float = 1.2,
    electrical_efficiency: float = 0.90,
    grid_region: GridRegion = "BRASIL_SIN",
) -> MachiningSustainabilityAuditPayload:
    """Apply a tabulated grid factor to a deterministic two-state energy model."""
    motor_power = _positive(motor_power_kw, code="SUSTAINABILITY_MOTOR_POWER_INVALID")
    standby_power = _positive(standby_power_kw, code="SUSTAINABILITY_STANDBY_POWER_INVALID")
    cutting_minutes = _nonnegative(
        cutting_time_minutes, code="SUSTAINABILITY_CUTTING_TIME_INVALID"
    )
    total_minutes = _nonnegative(
        total_cycle_time_minutes, code="SUSTAINABILITY_TOTAL_TIME_INVALID"
    )
    efficiency = _positive(
        electrical_efficiency, code="SUSTAINABILITY_ELECTRICAL_EFFICIENCY_INVALID"
    )
    if efficiency > 1:
        raise ValueError("SUSTAINABILITY_ELECTRICAL_EFFICIENCY_INVALID")
    if total_minutes < cutting_minutes:
        raise ValueError("SUSTAINABILITY_TIME_DECOMPOSITION_INVALID")
    try:
        emission_factor = _GRID_FACTORS[grid_region]
    except KeyError as exc:
        raise ValueError("SUSTAINABILITY_GRID_REGION_UNSUPPORTED") from exc
    cutting_energy = motor_power * (cutting_minutes / 60) / efficiency
    standby_energy = standby_power * ((total_minutes - cutting_minutes) / 60) / efficiency
    total_energy = cutting_energy + standby_energy
    return MachiningSustainabilityAuditPayload(
        grid_region=grid_region,
        grid_emission_factor_kg_co2e_per_kwh=emission_factor,
        motor_power_kw=motor_power,
        standby_power_kw=standby_power,
        cutting_time_minutes=cutting_minutes,
        total_cycle_time_minutes=total_minutes,
        electrical_efficiency=efficiency,
        cutting_energy_kwh=round(cutting_energy, 9),
        standby_energy_kwh=round(standby_energy, 9),
        electrical_energy_kwh=round(total_energy, 9),
        carbon_emission_kg_co2e=round(total_energy * emission_factor, 9),
    )


__all__ = ("estimate_sustainability",)
