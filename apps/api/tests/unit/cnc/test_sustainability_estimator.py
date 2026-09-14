import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import MachiningSustainabilityAuditPayload
from app.modules.cnc.services.sustainability_estimator import estimate_sustainability


@pytest.mark.parametrize(
    ("region", "factor"),
    (("BRASIL_SIN", 0.085), ("USA_AVG", 0.385), ("EU_AVG", 0.230)),
)
def test_energy_and_carbon_match_regional_factors(region, factor):
    result = estimate_sustainability(
        motor_power_kw=6,
        standby_power_kw=1.2,
        cutting_time_minutes=30,
        total_cycle_time_minutes=60,
        electrical_efficiency=0.9,
        grid_region=region,
    )
    expected_cutting = 6 * 0.5 / 0.9
    expected_standby = 1.2 * 0.5 / 0.9
    assert result.cutting_energy_kwh == pytest.approx(expected_cutting)
    assert result.standby_energy_kwh == pytest.approx(expected_standby)
    assert result.electrical_energy_kwh == pytest.approx(expected_cutting + expected_standby)
    assert result.carbon_emission_kg_co2e == pytest.approx(
        (expected_cutting + expected_standby) * factor
    )


@pytest.mark.parametrize(
    ("updates", "code"),
    (
        ({"motor_power_kw": 0}, "SUSTAINABILITY_MOTOR_POWER_INVALID"),
        ({"standby_power_kw": -1}, "SUSTAINABILITY_STANDBY_POWER_INVALID"),
        ({"cutting_time_minutes": -1}, "SUSTAINABILITY_CUTTING_TIME_INVALID"),
        ({"total_cycle_time_minutes": -1}, "SUSTAINABILITY_TOTAL_TIME_INVALID"),
        ({"electrical_efficiency": 0}, "SUSTAINABILITY_ELECTRICAL_EFFICIENCY_INVALID"),
        ({"electrical_efficiency": 1.1}, "SUSTAINABILITY_ELECTRICAL_EFFICIENCY_INVALID"),
        ({"grid_region": "UNKNOWN"}, "SUSTAINABILITY_GRID_REGION_UNSUPPORTED"),
    ),
)
def test_invalid_physical_or_conversion_inputs_fail_closed(updates, code):
    values = {
        "motor_power_kw": 6,
        "cutting_time_minutes": 30,
        "total_cycle_time_minutes": 60,
    }
    values.update(updates)
    with pytest.raises(ValueError, match=code):
        estimate_sustainability(**values)  # type: ignore[arg-type]


def test_cutting_time_cannot_exceed_cycle_and_payload_cannot_be_forged():
    with pytest.raises(ValueError, match="SUSTAINABILITY_TIME_DECOMPOSITION_INVALID"):
        estimate_sustainability(
            motor_power_kw=6, cutting_time_minutes=61, total_cycle_time_minutes=60
        )
    body = estimate_sustainability(
        motor_power_kw=6, cutting_time_minutes=30, total_cycle_time_minutes=60
    ).model_dump()
    body["carbon_emission_kg_co2e"] += 1
    with pytest.raises(ValidationError, match="CARBON_EMISSION_INCONSISTENT"):
        MachiningSustainabilityAuditPayload.model_validate(body)
