import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import SpindleBearingThermalAuditPayload
from app.modules.cnc.services.guideway_load_auditor import audit_guideway_load
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.spindle_bearing_auditor import (
    SpindleBearingAuditError,
    audit_spindle_bearing_thermal_load,
)


def _guideway(*, feed_mm_per_rev: float = 0.30, depth_of_cut_mm: float = 3.0):
    kienzle = estimate_cutting_power_force(
        "ABNT 1045",
        feed_mm_per_rev=feed_mm_per_rev,
        depth_of_cut_mm=depth_of_cut_mm,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=3_000.0,
        max_spindle_rpm=20_000.0,
        machine_power_limit_kw=100.0,
    )
    return audit_guideway_load(
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


def _audit(**overrides: object):
    values: dict[str, object] = {
        "source_guideway_load_audit": _guideway(),
        "internal_preload_n": 1_500.0,
        "load_friction_factor_f1": 0.0005,
        "viscous_friction_factor_f0": 2.0,
        "bearing_mean_diameter_mm": 70.0,
        "lubricant_kinematic_viscosity_mm2_s": 20.0,
        "operating_rpm": 3_000.0,
        "convection_coefficient_w_m2_k": 50.0,
        "housing_dissipation_area_m2": 0.08,
        "max_admissible_temp_c": 70.0,
    }
    values.update(overrides)
    return audit_spindle_bearing_thermal_load(**values)  # type: ignore[arg-type]


def test_high_speed_palmgren_torques_and_thermal_balance_are_deterministic() -> None:
    audit = _audit()
    source = audit.source_guideway_load_audit
    expected_load = math.sqrt(
        source.tangential_cutting_force_n**2
        + source.axial_feed_force_n**2
        + source.radial_cutting_force_n**2
    ) + 1_500.0
    expected_load_torque = 0.0005 * expected_load * 70.0 / 1_000.0
    expected_viscous_torque = (
        1e-7 * 2.0 * (20.0 * 3_000.0) ** (2.0 / 3.0) * 70.0**3 / 1_000.0
    )
    expected_total_torque = expected_load_torque + expected_viscous_torque
    expected_heat = expected_total_torque * 2.0 * math.pi * 3_000.0 / 60.0
    expected_rise = expected_heat / (50.0 * 0.08)

    assert audit.combined_equivalent_load_n == pytest.approx(expected_load)
    assert audit.load_torque_nm == pytest.approx(expected_load_torque)
    assert audit.viscous_torque_nm == pytest.approx(expected_viscous_torque)
    assert audit.total_friction_torque_nm == pytest.approx(expected_total_torque)
    assert audit.total_heat_dissipated_w == pytest.approx(expected_heat)
    assert audit.steady_state_temperature_rise_c == pytest.approx(expected_rise)
    assert audit.estimated_bearing_temp_c == pytest.approx(20.0 + expected_rise)
    assert audit.bearing_status == "SPINDLE_BEARING_THERMAL_COMPLIANT"
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert SpindleBearingThermalAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


def test_low_viscosity_speed_uses_palmgren_constant_branch() -> None:
    audit = _audit(
        lubricant_kinematic_viscosity_mm2_s=0.1,
        operating_rpm=1_000.0,
    )
    expected_viscous_torque = 160e-7 * 2.0 * 70.0**3 / 1_000.0

    assert 0.1 * 1_000.0 < 2_000.0
    assert audit.viscous_torque_nm == pytest.approx(expected_viscous_torque)


def test_continuous_near_ceiling_operation_without_forced_cooling_warns() -> None:
    audit = _audit(
        viscous_friction_factor_f0=10.0,
        bearing_mean_diameter_mm=100.0,
        lubricant_kinematic_viscosity_mm2_s=100.0,
        operating_rpm=12_000.0,
        convection_coefficient_w_m2_k=5.0,
        housing_dissipation_area_m2=0.01,
    )

    assert audit.estimated_bearing_temp_c > audit.max_admissible_temp_c
    assert audit.bearing_status == "SPINDLE_BEARING_OVERHEATING_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("operating_rpm", 0.0, "SPINDLE_BEARING_OPERATING_RPM_INVALID"),
        (
            "operating_rpm",
            20_001.0,
            "SPINDLE_BEARING_OPERATING_RPM_OUTSIDE_ENVELOPE",
        ),
        ("lubricant_kinematic_viscosity_mm2_s", 0.0, "SPINDLE_BEARING_VISCOSITY_INVALID"),
        ("lubricant_kinematic_viscosity_mm2_s", None, "SPINDLE_BEARING_VISCOSITY_INVALID"),
        ("internal_preload_n", None, "SPINDLE_BEARING_INTERNAL_PRELOAD_REQUIRED"),
        ("internal_preload_n", -1.0, "SPINDLE_BEARING_INTERNAL_PRELOAD_REQUIRED"),
        ("housing_dissipation_area_m2", 0.0, "SPINDLE_BEARING_HOUSING_AREA_INVALID"),
    ],
)
def test_nonphysical_bearing_parameters_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(SpindleBearingAuditError, match=code):
        _audit(**{field: value})


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("load_torque_nm", 1.0, "SPINDLE_BEARING_LOAD_TORQUE_INCONSISTENT"),
        ("viscous_torque_nm", 1.0, "SPINDLE_BEARING_VISCOUS_TORQUE_INCONSISTENT"),
        ("total_heat_dissipated_w", 1.0, "SPINDLE_BEARING_HEAT_INCONSISTENT"),
        (
            "estimated_bearing_temp_c",
            21.0,
            "SPINDLE_BEARING_TEMPERATURE_INCONSISTENT",
        ),
        (
            "bearing_status",
            "SPINDLE_BEARING_OVERHEATING_WARNING",
            "SPINDLE_BEARING_STATUS_INCONSISTENT",
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
        SpindleBearingThermalAuditPayload.model_validate(body)


def test_replayed_contract_rejects_transplanted_guideway_snapshot() -> None:
    body = _audit().model_dump()
    body["source_guideway_load_audit"] = _guideway(
        feed_mm_per_rev=0.8,
        depth_of_cut_mm=8.0,
    ).model_dump()
    with pytest.raises(
        ValidationError,
        match="SPINDLE_BEARING_EQUIVALENT_LOAD_INCONSISTENT",
    ):
        SpindleBearingThermalAuditPayload.model_validate(body)


def test_replayed_contract_rejects_rpm_outside_source_envelope() -> None:
    body = _audit().model_dump()
    body["operating_rpm"] = 20_001.0
    with pytest.raises(
        ValidationError,
        match="SPINDLE_BEARING_OPERATING_RPM_OUTSIDE_ENVELOPE",
    ):
        SpindleBearingThermalAuditPayload.model_validate(body)
