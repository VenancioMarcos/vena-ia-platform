import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import CycleTimeEstimatePayload, ToolLifeTaylorAuditPayload
from app.modules.cnc.services.cost_time_estimator import estimate_machining_cost_time
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


def _cycle(cutting_seconds: float = 120, rapid_seconds: float = 30):
    return CycleTimeEstimatePayload(
        total_cutting_time_seconds=cutting_seconds,
        total_rapid_time_seconds=rapid_seconds,
        total_cycle_time_seconds=cutting_seconds + rapid_seconds,
        total_cutting_distance_mm=40,
        total_rapid_distance_mm=10,
        rapid_feed_rate_mm_min=10_000,
        per_tool_breakdown=(),
    )


def _life(tool: str = "T0101", cutting_minutes: float = 2):
    return estimate_tool_life(
        tool,
        "Aço ABNT 1045",
        cutting_speed_m_per_min=200,
        effective_cutting_time_minutes=cutting_minutes,
    )


def test_cost_time_breakdown_matches_exact_formula():
    result = estimate_machining_cost_time(_cycle(), (_life(),))
    life = (350 / 200) ** (1 / 0.25)
    expected_machine = (2 + 0.5 + 15) / 60 * 120
    expected_tooling = 2 / life * 15
    assert result.total_cycle_time_minutes == pytest.approx(17.5)
    assert result.machine_cost_component == pytest.approx(expected_machine)
    assert result.tooling_wear_cost_component == pytest.approx(expected_tooling)
    assert result.estimated_total_cost == pytest.approx(expected_machine + expected_tooling)
    assert result.currency == "BRL"
    assert result.is_theoretical_estimate is True
    assert result.physical_use_authorized is False


def test_multiple_setups_and_tool_changes_are_accounted_for():
    result = estimate_machining_cost_time(
        _cycle(180, 60),
        (_life("T0101", 2), _life("T0202", 1)),
        setup_count=2,
        nominal_setup_time_minutes_each=12,
        tool_change_count=3,
        tool_change_time_minutes_each=0.75,
    )
    assert result.cutting_time_minutes == 3
    assert result.rapid_time_minutes == 1
    assert result.nominal_setup_time_minutes == 24
    assert result.tool_change_time_minutes == 2.25
    assert result.total_cycle_time_minutes == 30.25
    assert len(result.per_tool_wear_costs) == 2


@pytest.mark.parametrize(
    ("updates", "code"),
    (
        ({"setup_count": -1}, "COST_TIME_SETUP_COUNT_INVALID"),
        ({"nominal_setup_time_minutes_each": -1}, "COST_TIME_SETUP_DURATION_INVALID"),
        ({"tool_change_count": -1}, "COST_TIME_TOOL_CHANGE_COUNT_INVALID"),
        ({"tool_change_time_minutes_each": -1}, "COST_TIME_TOOL_CHANGE_DURATION_INVALID"),
        ({"cost_profile": "EUR"}, "COST_TIME_PROFILE_UNSUPPORTED"),
    ),
)
def test_invalid_financial_or_time_parameters_fail_closed(updates, code):
    with pytest.raises(ValueError, match=code):
        estimate_machining_cost_time(_cycle(), (_life(),), **updates)  # type: ignore[arg-type]


def test_missing_or_zero_tool_life_and_forged_totals_are_rejected():
    with pytest.raises(ValueError, match="COST_TIME_TOOL_LIFE_REQUIRED"):
        estimate_machining_cost_time(_cycle(), ())
    life_body = _life().model_dump()
    life_body["estimated_tool_life_minutes"] = 0
    with pytest.raises(ValidationError):
        ToolLifeTaylorAuditPayload.model_validate(life_body)
    body = estimate_machining_cost_time(_cycle(), (_life(),)).model_dump()
    body["estimated_total_cost"] += 1
    with pytest.raises(ValidationError, match="TOTAL_COST_INCONSISTENT"):
        type(estimate_machining_cost_time(_cycle(), (_life(),))).model_validate(body)
