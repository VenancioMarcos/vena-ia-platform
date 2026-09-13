import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ToolLifeTaylorAuditPayload
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


def _estimate(speed: float = 200.0, **updates: object):
    values: dict[str, object] = {
        "cutting_speed_m_per_min": speed,
        "effective_cutting_time_minutes": 2.0,
    }
    values.update(updates)
    return estimate_tool_life("T0101", "Aço ABNT 1045", **values)  # type: ignore[arg-type]


@pytest.mark.parametrize("speed", (150.0, 200.0, 250.0))
def test_taylor_life_matches_canonical_equation(speed):
    result = _estimate(speed)
    expected = (350.0 / speed) ** (1 / 0.25)
    assert result.estimated_tool_life_minutes == pytest.approx(expected)
    assert result.tool_life_consumed_percent == pytest.approx(2 / expected * 100)
    assert result.integrity_status == (
        "TOOL_LIFE_SAFE" if 2 / expected * 100 <= 80 else "TOOL_LIFE_EXHAUSTED_WARNING"
    )
    assert result.is_theoretical_model is True
    assert result.physical_use_authorized is False


def test_aluminum_pair_and_critical_wear_warning():
    aluminum = estimate_tool_life(
        "T0202",
        "Alumínio 6061-T6",
        cutting_speed_m_per_min=400,
        effective_cutting_time_minutes=30,
    )
    assert aluminum.tool_material_pair == "CARBIDE_K10_ALUMINUM_6061_T6"
    critical = _estimate(250, effective_cutting_time_minutes=4)
    assert critical.tool_life_consumed_percent > 80
    assert critical.integrity_status == "TOOL_LIFE_EXHAUSTED_WARNING"


@pytest.mark.parametrize(
    ("updates", "code"),
    (
        ({"cutting_speed_m_per_min": 0}, "TAYLOR_CUTTING_SPEED_INVALID"),
        ({"taylor_n": 0}, "TAYLOR_N_INVALID"),
        ({"taylor_n": 1}, "TAYLOR_N_INVALID"),
        ({"taylor_c": -1}, "TAYLOR_C_INVALID"),
        ({"effective_cutting_time_minutes": -1}, "TAYLOR_CUTTING_TIME_INVALID"),
    ),
)
def test_nonphysical_inputs_fail_closed(updates, code):
    with pytest.raises(ValueError, match=code):
        _estimate(**updates)


def test_missing_tool_unsupported_pair_and_forged_payload_are_rejected():
    with pytest.raises(ValueError, match="TAYLOR_TOOL_REQUIRED"):
        estimate_tool_life(
            "", "Aço ABNT 1045", cutting_speed_m_per_min=200, effective_cutting_time_minutes=1
        )
    with pytest.raises(ValueError, match="TAYLOR_TOOL_MATERIAL_PAIR_UNSUPPORTED"):
        estimate_tool_life(
            "T1", "unknown", cutting_speed_m_per_min=200, effective_cutting_time_minutes=1
        )
    body = _estimate().model_dump()
    body["estimated_tool_life_minutes"] *= 2
    with pytest.raises(ValidationError, match="TAYLOR_TOOL_LIFE_INCONSISTENT"):
        ToolLifeTaylorAuditPayload.model_validate(body)


def test_taylor_payload_rejects_non_tabulated_profile_parameters():
    body = _estimate().model_dump()
    body["taylor_c"] = 400.0
    with pytest.raises(ValidationError, match="TAYLOR_PROFILE_PARAMETERS_INCONSISTENT"):
        ToolLifeTaylorAuditPayload.model_validate(body)
