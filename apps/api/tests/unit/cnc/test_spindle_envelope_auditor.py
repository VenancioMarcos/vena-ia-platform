import math

import pytest

from app.modules.cnc.schemas import SpindlePowerTorqueCurvePoint
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.spindle_envelope_auditor import (
    audit_spindle_power_torque_envelope,
    declared_spindle_curve,
)


def _source(*, rpm: float = 1_000.0, power_limit: float = 7.5):
    return estimate_cutting_power_force(
        "Aço ABNT 1045",
        feed_mm_per_rev=0.2,
        depth_of_cut_mm=0.5,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=rpm,
        max_spindle_rpm=3_000.0,
        machine_power_limit_kw=power_limit,
    )


def _point(rpm: float, torque: float) -> SpindlePowerTorqueCurvePoint:
    return SpindlePowerTorqueCurvePoint(
        spindle_rpm=rpm,
        available_torque_nm=torque,
        available_power_kw=torque * 2.0 * math.pi * rpm / 60_000.0,
    )


def test_interpolates_constant_torque_low_speed_regime() -> None:
    source = _source(rpm=750.0)
    audit = audit_spindle_power_torque_envelope(
        source,
        (_point(500.0, 50.0), _point(1_000.0, 50.0), _point(3_000.0, 16.666666667)),
    )

    point = audit.operating_points[0]
    assert point.available_torque_nm == pytest.approx(50.0)
    assert point.available_power_kw == pytest.approx(3.926990817)
    assert point.power_margin_percent == pytest.approx(
        ((point.available_power_kw - source.pc_cutting_kw) / point.available_power_kw) * 100
    )


def test_declared_curve_preserves_constant_power_at_high_speed_endpoint() -> None:
    source = _source(rpm=3_000.0)
    curve = declared_spindle_curve(source)
    audit = audit_spindle_power_torque_envelope(source, curve)

    point = audit.operating_points[0]
    assert point.available_power_kw == pytest.approx(source.machine_power_limit_kw)
    assert point.available_torque_nm == pytest.approx(
        source.machine_power_limit_kw / (2.0 * math.pi * 3_000.0 / 60_000.0)
    )


def test_overload_returns_fail_closed_warning() -> None:
    source = _source()
    audit = audit_spindle_power_torque_envelope(
        source,
        (_point(500.0, 0.1), _point(3_000.0, 0.05)),
    )

    assert audit.audit_status == "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING"
    assert audit.operating_points[0].power_margin_percent < 0


@pytest.mark.parametrize("rpm", [0.0, -1.0, math.nan, math.inf])
def test_rejects_non_physical_operating_rpm(rpm: float) -> None:
    source = _source()
    curve = (_point(500.0, 50.0), _point(3_000.0, 20.0))

    with pytest.raises(ValueError, match="SPINDLE_OPERATING_RPM_INVALID"):
        audit_spindle_power_torque_envelope(source, curve, operating_rpms=(rpm,))


def test_rejects_non_monotonic_curve() -> None:
    source = _source()
    curve = (_point(3_000.0, 20.0), _point(500.0, 50.0))

    with pytest.raises(ValueError, match="SPINDLE_CURVE_RPM_ORDER_INVALID"):
        audit_spindle_power_torque_envelope(source, curve)
