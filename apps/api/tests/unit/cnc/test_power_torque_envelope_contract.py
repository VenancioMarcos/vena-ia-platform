import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import (
    SpindlePowerTorqueCurvePoint,
    SpindlePowerTorqueEnvelopeAuditPayload,
    SpindlePowerTorqueOperatingPoint,
)
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force


def _source():
    return estimate_cutting_power_force(
        "Aço ABNT 1045",
        feed_mm_per_rev=0.2,
        depth_of_cut_mm=0.5,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=1_000.0,
        max_spindle_rpm=3_000.0,
        machine_power_limit_kw=7.5,
    )


def _curve_point(rpm: float, torque_nm: float) -> SpindlePowerTorqueCurvePoint:
    return SpindlePowerTorqueCurvePoint(
        spindle_rpm=rpm,
        available_torque_nm=torque_nm,
        available_power_kw=torque_nm * 2.0 * math.pi * rpm / 60_000.0,
    )


def _operating_point(
    *,
    rpm: float,
    required_power_kw: float,
    available_torque_nm: float,
) -> SpindlePowerTorqueOperatingPoint:
    angular_factor = 2.0 * math.pi * rpm / 60_000.0
    required_torque = required_power_kw / angular_factor
    available_power = available_torque_nm * angular_factor
    power_margin = available_power - required_power_kw
    torque_margin = available_torque_nm - required_torque
    return SpindlePowerTorqueOperatingPoint(
        spindle_rpm=rpm,
        required_cutting_power_kw=required_power_kw,
        required_torque_nm=required_torque,
        available_power_kw=available_power,
        available_torque_nm=available_torque_nm,
        power_margin_kw=power_margin,
        power_margin_percent=(power_margin / available_power) * 100.0,
        torque_margin_nm=torque_margin,
        status=(
            "WITHIN_POWER_TORQUE_ENVELOPE"
            if power_margin >= 0 and torque_margin >= 0
            else "POWER_TORQUE_ENVELOPE_EXCEEDED"
        ),
    )


def _payload(
    *,
    lower_torque_nm: float = 100.0,
    upper_torque_nm: float = 20.0,
) -> SpindlePowerTorqueEnvelopeAuditPayload:
    source = _source()
    expected_torque_at_reference = lower_torque_nm + (upper_torque_nm - lower_torque_nm) * (
        (source.spindle_rpm_reference - 500.0) / (3_000.0 - 500.0)
    )
    operating = _operating_point(
        rpm=source.spindle_rpm_reference,
        required_power_kw=source.pc_cutting_kw,
        available_torque_nm=expected_torque_at_reference,
    )
    return SpindlePowerTorqueEnvelopeAuditPayload(
        source_power_force_audit=source,
        spindle_rpm_min=500.0,
        spindle_rpm_max=3_000.0,
        curve_points=(
            _curve_point(500.0, lower_torque_nm),
            _curve_point(3_000.0, upper_torque_nm),
        ),
        operating_points=(operating,),
        audit_status=(
            "POWER_TORQUE_ENVELOPE_COMPLIANT"
            if operating.status == "WITHIN_POWER_TORQUE_ENVELOPE"
            else "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING"
        ),
    )


def test_v2_pydantic_contract_accepts_traceable_interpolated_envelope() -> None:
    audit = _payload()

    assert audit.schema_version == "vena-ia.cnc-spindle-power-torque-envelope-audit/v2"
    assert audit.audit_status == "POWER_TORQUE_ENVELOPE_COMPLIANT"
    assert audit.operating_points[0].available_torque_nm == pytest.approx(84.0)
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert audit.safety_flags.executable_output is False
    assert SpindlePowerTorqueEnvelopeAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


def test_insufficient_declared_torque_fails_closed_with_warning_status() -> None:
    audit = _payload(lower_torque_nm=0.1, upper_torque_nm=0.05)

    assert audit.operating_points[0].status == "POWER_TORQUE_ENVELOPE_EXCEEDED"
    assert audit.audit_status == "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING"


def test_curve_rpm_points_must_be_strictly_increasing() -> None:
    body = _payload().model_dump()
    body["curve_points"] = tuple(reversed(body["curve_points"]))

    with pytest.raises(ValidationError, match="SPINDLE_CURVE_RPM_ORDER_INVALID"):
        SpindlePowerTorqueEnvelopeAuditPayload.model_validate(body)


def test_operating_point_must_match_interpolated_curve() -> None:
    audit = _payload()
    body = audit.model_dump()
    source_power = audit.source_power_force_audit.pc_cutting_kw
    body["operating_points"] = (
        _operating_point(
            rpm=1_000.0,
            required_power_kw=source_power,
            available_torque_nm=80.0,
        ).model_dump(),
    )

    with pytest.raises(ValidationError, match="SPINDLE_CURVE_INTERPOLATION_INCONSISTENT"):
        SpindlePowerTorqueEnvelopeAuditPayload.model_validate(body)


def test_reference_rpm_and_power_force_snapshot_are_mandatory() -> None:
    audit = _payload()
    body = audit.model_dump()
    second = _operating_point(
        rpm=1_500.0,
        required_power_kw=audit.source_power_force_audit.pc_cutting_kw,
        available_torque_nm=68.0,
    )
    body["operating_points"] = (second.model_dump(),)

    with pytest.raises(ValidationError, match="SPINDLE_REFERENCE_RPM_NOT_AUDITED"):
        SpindlePowerTorqueEnvelopeAuditPayload.model_validate(body)
