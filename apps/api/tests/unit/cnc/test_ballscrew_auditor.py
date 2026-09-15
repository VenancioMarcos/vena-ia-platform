import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import BallscrewAxialMechanicsAuditPayload
from app.modules.cnc.services.ballscrew_auditor import (
    BallscrewAuditError,
    audit_ballscrew_mechanics,
)
from app.modules.cnc.services.guideway_load_auditor import audit_guideway_load
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force


def _guideway(*, feed_mm_per_rev: float = 0.30, depth_of_cut_mm: float = 3.0):
    kienzle = estimate_cutting_power_force(
        "ABNT 1045",
        feed_mm_per_rev=feed_mm_per_rev,
        depth_of_cut_mm=depth_of_cut_mm,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=1_200.0,
        max_spindle_rpm=6_000.0,
        machine_power_limit_kw=30.0,
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
        "guide_friction_coefficient": 0.003,
        "carriage_mass_kg": 400.0,
        "carriage_acceleration_m_s2": 1.5,
        "ballscrew_root_diameter_mm": 32.0,
        "ballscrew_lead_mm_per_rev": 10.0,
        "ballscrew_length_mm": 1_000.0,
        "young_modulus_mpa": 210_000.0,
        "buckling_mounting_factor": 1.0,
        "critical_speed_mounting_factor": 1.0,
        "axial_feed_rate_mm_per_min": 300.0,
    }
    values.update(overrides)
    return audit_ballscrew_mechanics(**values)  # type: ignore[arg-type]


def test_typical_32_mm_root_10_mm_lead_and_1000_mm_length() -> None:
    audit = _audit()
    source = audit.source_guideway_load_audit
    expected_inertia = math.pi * 32.0**4 / 64.0
    expected_thrust = (
        source.axial_feed_force_n
        + 0.003 * (400.0 * 9.80665 + source.radial_cutting_force_n)
        + 400.0 * 1.5
    )
    expected_euler = math.pi**2 * 210_000.0 * expected_inertia / 1_000.0**2

    assert audit.area_moment_of_inertia_mm4 == pytest.approx(expected_inertia)
    assert audit.total_axial_thrust_n == pytest.approx(expected_thrust)
    assert audit.euler_buckling_limit_n == pytest.approx(expected_euler)
    assert audit.critical_speed_rpm == pytest.approx(320.0)
    assert audit.operating_ballscrew_rpm == pytest.approx(30.0)
    assert audit.load_ratio_percent == pytest.approx(expected_thrust / expected_euler * 100)
    assert audit.speed_ratio_percent == pytest.approx(30.0 / 320.0 * 100)
    assert audit.ballscrew_status == "BALLSCREW_MECHANICS_COMPLIANT"
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert BallscrewAxialMechanicsAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_heavy_interrupted_feed_warns_for_axial_buckling() -> None:
    audit = _audit(
        source_guideway_load_audit=_guideway(
            feed_mm_per_rev=0.8,
            depth_of_cut_mm=8.0,
        ),
        carriage_mass_kg=1_500.0,
        carriage_acceleration_m_s2=8.0,
        ballscrew_root_diameter_mm=12.0,
        ballscrew_length_mm=2_000.0,
    )

    assert audit.total_axial_thrust_n > 0.5 * audit.euler_buckling_limit_n
    assert audit.ballscrew_status == "BALLSCREW_AXIAL_BUCKLING_RISK_WARNING"


def test_extrapolated_g00_warns_for_critical_speed() -> None:
    audit = _audit(axial_feed_rate_mm_per_min=3_000.0)

    assert audit.operating_ballscrew_rpm > 0.8 * audit.critical_speed_rpm
    assert audit.total_axial_thrust_n <= 0.5 * audit.euler_buckling_limit_n
    assert audit.ballscrew_status == "BALLSCREW_CRITICAL_SPEED_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("ballscrew_root_diameter_mm", None, "BALLSCREW_ROOT_DIAMETER_INVALID"),
        ("ballscrew_root_diameter_mm", -1.0, "BALLSCREW_ROOT_DIAMETER_INVALID"),
        ("ballscrew_length_mm", 0.0, "BALLSCREW_LENGTH_INVALID"),
        (
            "buckling_mounting_factor",
            None,
            "BALLSCREW_BUCKLING_MOUNTING_FACTOR_REQUIRED",
        ),
        (
            "critical_speed_mounting_factor",
            0.0,
            "BALLSCREW_SPEED_MOUNTING_FACTOR_REQUIRED",
        ),
    ],
)
def test_invalid_mechanical_parameters_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(BallscrewAuditError, match=code):
        _audit(**{field: value})


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        (
            "total_axial_thrust_n",
            1.0,
            "BALLSCREW_TOTAL_AXIAL_THRUST_INCONSISTENT",
        ),
        (
            "critical_speed_rpm",
            1.0,
            "BALLSCREW_CRITICAL_SPEED_INCONSISTENT",
        ),
        ("load_ratio_percent", 1.0, "BALLSCREW_LOAD_RATIO_INCONSISTENT"),
        (
            "ballscrew_status",
            "BALLSCREW_CRITICAL_SPEED_WARNING",
            "BALLSCREW_STATUS_INCONSISTENT",
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
        BallscrewAxialMechanicsAuditPayload.model_validate(body)


def test_replayed_contract_rejects_transplanted_guideway_snapshot() -> None:
    body = _audit().model_dump()
    transplanted = _guideway(feed_mm_per_rev=0.8, depth_of_cut_mm=8.0)
    body["source_guideway_load_audit"] = transplanted.model_dump()
    with pytest.raises(
        ValidationError,
        match="BALLSCREW_TOTAL_AXIAL_THRUST_INCONSISTENT",
    ):
        BallscrewAxialMechanicsAuditPayload.model_validate(body)
