import math
from typing import Literal

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import SpindleBearingLifeAuditPayload
from app.modules.cnc.services.bearing_life_auditor import (
    BearingLifeAuditError,
    audit_spindle_bearing_l10h_life,
)
from app.modules.cnc.services.guideway_load_auditor import audit_guideway_load
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.spindle_bearing_auditor import (
    audit_spindle_bearing_thermal_load,
)


def _thermal(*, operating_rpm: float = 3_000.0):
    kienzle = estimate_cutting_power_force(
        "ABNT 1045",
        feed_mm_per_rev=0.30,
        depth_of_cut_mm=3.0,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=3_000.0,
        max_spindle_rpm=20_000.0,
        machine_power_limit_kw=100.0,
    )
    guideway = audit_guideway_load(
        kienzle,
        feed_force_ratio=0.30,
        radial_force_ratio=0.50,
        lever_arm_x_mm=120.0,
        lever_arm_y_mm=180.0,
        lever_arm_z_mm=220.0,
        block_spacing_x_mm=240.0,
        rail_spacing_y_mm=300.0,
        block_spacing_z_mm=360.0,
        static_capacity_n=80_000.0,
    )
    return audit_spindle_bearing_thermal_load(
        guideway,
        internal_preload_n=1_500.0,
        load_friction_factor_f1=0.0005,
        viscous_friction_factor_f0=2.0,
        bearing_mean_diameter_mm=70.0,
        lubricant_kinematic_viscosity_mm2_s=20.0,
        operating_rpm=operating_rpm,
        convection_coefficient_w_m2_k=50.0,
        housing_dissipation_area_m2=0.08,
        max_admissible_temp_c=70.0,
    )


def _audit(**overrides: object):
    values: dict[str, object] = {
        "source_spindle_bearing_thermal_audit": _thermal(),
        "bearing_type": "ANGULAR_CONTACT_BALL",
        "axial_preload_n": 1_500.0,
        "radial_load_factor_x": 1.0,
        "axial_load_factor_y": 1.0,
        "dynamic_capacity_c_n": 100_000.0,
        "required_kinematic_viscosity_nu1_mm2_s": 12.0,
        "minimum_admissible_l10h_hours": 5_000.0,
    }
    values.update(overrides)
    return audit_spindle_bearing_l10h_life(**values)  # type: ignore[arg-type]


def test_angular_contact_ball_l10_and_l10h_are_exact() -> None:
    audit = _audit()
    expected_basic_l10 = (
        audit.dynamic_capacity_c_n / audit.equivalent_dynamic_load_n
    ) ** 3.0
    expected_l10 = audit.a_iso_modification_factor * expected_basic_l10
    expected_l10h = 1_000_000.0 * expected_l10 / (60.0 * audit.operating_rpm)

    assert audit.life_exponent_p == 3.0
    assert audit.basic_l10_million_revs == pytest.approx(expected_basic_l10)
    assert audit.l10_million_revs == pytest.approx(expected_l10)
    assert audit.l10h_hours == pytest.approx(expected_l10h)
    assert audit.bearing_life_status == "BEARING_FATIGUE_LIFE_COMPLIANT"
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert SpindleBearingLifeAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


@pytest.mark.parametrize("bearing_type", ["CYLINDRICAL_ROLLER", "TAPERED_ROLLER"])
def test_roller_l10_and_l10h_use_ten_thirds_exponent(
    bearing_type: Literal["CYLINDRICAL_ROLLER", "TAPERED_ROLLER"],
) -> None:
    audit = _audit(bearing_type=bearing_type)
    expected_basic_l10 = (
        audit.dynamic_capacity_c_n / audit.equivalent_dynamic_load_n
    ) ** (10.0 / 3.0)
    expected_l10 = audit.a_iso_modification_factor * expected_basic_l10

    assert audit.life_exponent_p == pytest.approx(10.0 / 3.0)
    assert audit.basic_l10_million_revs == pytest.approx(expected_basic_l10)
    assert audit.l10_million_revs == pytest.approx(expected_l10)
    assert audit.l10h_hours == pytest.approx(
        1_000_000.0 * expected_l10 / (60.0 * audit.operating_rpm)
    )


def test_heavy_continuous_high_rpm_operation_warns_of_premature_fatigue() -> None:
    audit = _audit(
        source_spindle_bearing_thermal_audit=_thermal(operating_rpm=12_000.0),
        dynamic_capacity_c_n=3_000.0,
    )

    assert audit.l10h_hours < audit.minimum_admissible_l10h_hours
    assert audit.bearing_life_status == "PREMATURE_BEARING_FATIGUE_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("dynamic_capacity_c_n", None, "BEARING_LIFE_DYNAMIC_CAPACITY_REQUIRED"),
        ("dynamic_capacity_c_n", math.nan, "BEARING_LIFE_DYNAMIC_CAPACITY_REQUIRED"),
        ("dynamic_capacity_c_n", 0.0, "BEARING_LIFE_DYNAMIC_CAPACITY_REQUIRED"),
        ("radial_load_factor_x", 0.0, "BEARING_LIFE_RADIAL_FACTOR_INVALID"),
        (
            "required_kinematic_viscosity_nu1_mm2_s",
            math.inf,
            "BEARING_LIFE_REQUIRED_VISCOSITY_INVALID",
        ),
    ],
)
def test_nonphysical_or_nonfinite_parameters_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(BearingLifeAuditError, match=code):
        _audit(**{field: value})


def test_corrupt_nonfinite_source_geometry_fails_closed() -> None:
    corrupted = _thermal().model_dump()
    corrupted["source_guideway_load_audit"]["radial_cutting_force_n"] = math.nan

    with pytest.raises(BearingLifeAuditError, match="BEARING_LIFE_THERMAL_SOURCE_INVALID"):
        _audit(source_spindle_bearing_thermal_audit=corrupted)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("equivalent_dynamic_load_n", 1.0, "BEARING_LIFE_EQUIVALENT_LOAD_INCONSISTENT"),
        ("viscosity_ratio_kappa", 1.0, "BEARING_LIFE_KAPPA_INCONSISTENT"),
        ("l10_million_revs", 1.0, "BEARING_LIFE_L10_INCONSISTENT"),
        ("l10h_hours", 1.0, "BEARING_LIFE_L10H_INCONSISTENT"),
        (
            "bearing_life_status",
            "PREMATURE_BEARING_FATIGUE_WARNING",
            "BEARING_LIFE_STATUS_INCONSISTENT",
        ),
    ],
)
def test_replayed_contract_rejects_tampered_derivatives(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _audit().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        SpindleBearingLifeAuditPayload.model_validate(body)
