import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import MachiningPowerForceAuditPayload
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force


def _estimate(material: str = "Aço ABNT 1045", **updates: object):
    values: dict[str, object] = {
        "feed_mm_per_rev": 0.2,
        "depth_of_cut_mm": 2.0,
        "cutting_edge_angle_deg": 95.0,
        "cutting_speed_m_per_min": 180.0,
        "spindle_rpm_reference": 1_500.0,
        "max_spindle_rpm": 3_000.0,
        "machine_power_limit_kw": 7.5,
    }
    values.update(updates)
    return estimate_cutting_power_force(material, **values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("material", "profile", "kc1_1", "mc"),
    (
        ("Aço ABNT 1045", "ABNT_1045", 1_900.0, 0.26),
        ("Alumínio 6061-T6", "ALUMINUM_6061_T6", 700.0, 0.23),
    ),
)
def test_kienzle_matches_canonical_material_parameters(material, profile, kc1_1, mc):
    result = _estimate(material)
    sin_kr = math.sin(math.radians(95.0))
    width = 2.0 / sin_kr
    thickness = 0.2 * sin_kr
    force = kc1_1 * width * thickness ** (1 - mc)

    assert result.material_profile == profile
    assert result.fc_nominal_n == pytest.approx(force)
    assert result.pc_cutting_kw == pytest.approx(force * 180 / 60_000)
    assert result.p_motor_est_kw == pytest.approx(result.pc_cutting_kw / 0.80)
    assert result.mrr_cm3_min == pytest.approx(72.0)
    assert result.power_status == "POWER_WITHIN_LIMITS"
    assert result.is_theoretical_model is True
    assert result.physical_use_authorized is False


def test_power_warning_uses_configured_machine_limit():
    result = _estimate(machine_power_limit_kw=0.1)
    assert result.power_status == "POWER_EXCEEDED_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("feed_mm_per_rev", 0.0, "KIENZLE_FEED_INVALID"),
        ("depth_of_cut_mm", -1.0, "KIENZLE_DEPTH_INVALID"),
        ("cutting_edge_angle_deg", 180.0, "KIENZLE_CUTTING_EDGE_ANGLE_INVALID"),
        ("cutting_speed_m_per_min", float("nan"), "KIENZLE_CUTTING_SPEED_INVALID"),
        ("spindle_rpm_reference", 3_001.0, "KIENZLE_SPINDLE_RPM_EXCEEDS_LIMIT"),
        ("machine_power_limit_kw", False, "KIENZLE_POWER_LIMIT_INVALID"),
    ),
)
def test_nonphysical_or_out_of_limit_inputs_fail_closed(field, value, code):
    with pytest.raises(ValueError, match=code):
        _estimate(**{field: value})


def test_unknown_material_and_forged_payload_are_rejected():
    with pytest.raises(ValueError, match="MACHINING_MATERIAL_UNSUPPORTED"):
        _estimate("unknown alloy")

    body = _estimate().model_dump()
    body["fc_nominal_n"] *= 2
    with pytest.raises(ValidationError, match="KIENZLE_FORCE_INCONSISTENT"):
        MachiningPowerForceAuditPayload.model_validate(body)
