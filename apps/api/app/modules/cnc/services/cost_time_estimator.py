"""Deterministic analytical machining time and cost estimates."""

from math import fsum, isfinite
from typing import Literal

from app.modules.cnc.schemas import (
    CycleTimeEstimatePayload,
    MachiningCostTimeAuditPayload,
    ToolingWearCostComponent,
    ToolLifeTaylorAuditPayload,
)


CostProfile = Literal["BRL_STANDARD", "USD_STANDARD"]
_COST_PROFILES: dict[CostProfile, tuple[Literal["BRL", "USD"], float, float]] = {
    "BRL_STANDARD": ("BRL", 120.0, 15.0),
    "USD_STANDARD": ("USD", 25.0, 3.0),
}


def _nonnegative(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    result = float(value)
    if not isfinite(result) or result < 0:
        raise ValueError(code)
    return result


def _nonnegative_integer(value: int, *, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(code)
    return value


def estimate_machining_cost_time(
    cycle_time: CycleTimeEstimatePayload,
    tool_life_audits: tuple[ToolLifeTaylorAuditPayload, ...],
    *,
    setup_count: int = 1,
    nominal_setup_time_minutes_each: float = 15.0,
    tool_change_count: int | None = None,
    tool_change_time_minutes_each: float = 0.5,
    cost_profile: CostProfile = "BRL_STANDARD",
) -> MachiningCostTimeAuditPayload:
    """Combine path time, nominal overhead, machine rate, and Taylor wear cost."""
    validated_cycle = CycleTimeEstimatePayload.model_validate(cycle_time)
    validated_lives = tuple(
        ToolLifeTaylorAuditPayload.model_validate(item) for item in tool_life_audits
    )
    if not validated_lives:
        raise ValueError("COST_TIME_TOOL_LIFE_REQUIRED")
    try:
        currency, machine_rate, cutting_edge_cost = _COST_PROFILES[cost_profile]
    except KeyError as exc:
        raise ValueError("COST_TIME_PROFILE_UNSUPPORTED") from exc
    setups = _nonnegative_integer(setup_count, code="COST_TIME_SETUP_COUNT_INVALID")
    changes = (
        max(len(validated_lives) - 1, 0)
        if tool_change_count is None
        else _nonnegative_integer(tool_change_count, code="COST_TIME_TOOL_CHANGE_COUNT_INVALID")
    )
    setup_each = _nonnegative(
        nominal_setup_time_minutes_each, code="COST_TIME_SETUP_DURATION_INVALID"
    )
    change_each = _nonnegative(
        tool_change_time_minutes_each, code="COST_TIME_TOOL_CHANGE_DURATION_INVALID"
    )
    cutting_minutes = validated_cycle.total_cutting_time_seconds / 60.0
    rapid_minutes = validated_cycle.total_rapid_time_seconds / 60.0
    setup_minutes = setups * setup_each
    tool_change_minutes = changes * change_each
    total_minutes = cutting_minutes + rapid_minutes + setup_minutes + tool_change_minutes
    wear_items = tuple(
        ToolingWearCostComponent(
            tool_id=item.tool_id,
            effective_cutting_time_minutes=item.effective_cutting_time_minutes,
            estimated_tool_life_minutes=item.estimated_tool_life_minutes,
            consumed_fraction=round(
                item.effective_cutting_time_minutes / item.estimated_tool_life_minutes, 9
            ),
            cutting_edge_cost=cutting_edge_cost,
            estimated_wear_cost=round(
                item.effective_cutting_time_minutes
                / item.estimated_tool_life_minutes
                * cutting_edge_cost,
                9,
            ),
        )
        for item in validated_lives
    )
    machine_cost = total_minutes / 60.0 * machine_rate
    tooling_cost = fsum(item.estimated_wear_cost for item in wear_items)
    return MachiningCostTimeAuditPayload(
        cost_profile=cost_profile,
        total_cycle_time_minutes=round(total_minutes, 9),
        cutting_time_minutes=round(cutting_minutes, 9),
        rapid_time_minutes=round(rapid_minutes, 9),
        tool_change_count=changes,
        tool_change_time_minutes_each=change_each,
        tool_change_time_minutes=round(tool_change_minutes, 9),
        setup_count=setups,
        nominal_setup_time_minutes_each=setup_each,
        nominal_setup_time_minutes=round(setup_minutes, 9),
        estimated_total_cost=round(machine_cost + tooling_cost, 9),
        machine_cost_component=round(machine_cost, 9),
        tooling_wear_cost_component=round(tooling_cost, 9),
        machine_hourly_rate=machine_rate,
        cutting_edge_cost=cutting_edge_cost,
        currency=currency,
        per_tool_wear_costs=wear_items,
    )


__all__ = ("estimate_machining_cost_time",)
