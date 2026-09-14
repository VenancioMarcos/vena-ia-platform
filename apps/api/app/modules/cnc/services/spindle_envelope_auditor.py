"""Deterministic spindle power/torque envelope audit for analytical review."""

import math
from collections.abc import Iterable
from typing import Literal

from app.modules.cnc.schemas import (
    MachiningPowerForceAuditPayload,
    SpindlePowerTorqueCurvePoint,
    SpindlePowerTorqueEnvelopeAuditPayload,
    SpindlePowerTorqueOperatingPoint,
)


def _positive_finite(value: float, *, code: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(code)
    return float(value)


def declared_spindle_curve(
    power_force_audit: MachiningPowerForceAuditPayload,
) -> tuple[SpindlePowerTorqueCurvePoint, ...]:
    """Build a conservative declared curve from the reviewed machine power limit."""
    source = MachiningPowerForceAuditPayload.model_validate(power_force_audit)
    maximum_rpm = source.max_spindle_rpm
    minimum_rpm = min(source.spindle_rpm_reference, max(1.0, maximum_rpm * 0.05))
    if math.isclose(minimum_rpm, maximum_rpm, abs_tol=5e-9):
        minimum_rpm = maximum_rpm * 0.5
    base_rpm = min(max(minimum_rpm, maximum_rpm * 0.35), maximum_rpm)
    reference_rpm = source.spindle_rpm_reference
    rpms = sorted({minimum_rpm, base_rpm, reference_rpm, maximum_rpm})
    if len(rpms) < 2:
        raise ValueError("SPINDLE_CURVE_RANGE_INVALID")

    base_factor = 2.0 * math.pi * base_rpm / 60_000.0
    constant_torque_nm = source.machine_power_limit_kw / base_factor
    points = []
    for rpm in rpms:
        angular_factor = 2.0 * math.pi * rpm / 60_000.0
        torque_nm = (
            constant_torque_nm
            if rpm <= base_rpm
            else source.machine_power_limit_kw / angular_factor
        )
        points.append(
            SpindlePowerTorqueCurvePoint(
                spindle_rpm=rpm,
                available_torque_nm=torque_nm,
                available_power_kw=torque_nm * angular_factor,
            )
        )
    return tuple(points)


def audit_spindle_power_torque_envelope(
    power_force_audit: MachiningPowerForceAuditPayload,
    curve_points: Iterable[SpindlePowerTorqueCurvePoint],
    *,
    operating_rpms: Iterable[float] | None = None,
) -> SpindlePowerTorqueEnvelopeAuditPayload:
    """Interpolate a declared curve and compare it with the Kienzle power demand."""
    source = MachiningPowerForceAuditPayload.model_validate(power_force_audit)
    curve = tuple(SpindlePowerTorqueCurvePoint.model_validate(point) for point in curve_points)
    if len(curve) < 2:
        raise ValueError("SPINDLE_CURVE_POINTS_REQUIRED")
    if any(
        current.spindle_rpm >= following.spindle_rpm
        for current, following in zip(curve, curve[1:])
    ):
        raise ValueError("SPINDLE_CURVE_RPM_ORDER_INVALID")

    requested_rpms = tuple(
        operating_rpms if operating_rpms is not None else (source.spindle_rpm_reference,)
    )
    if not requested_rpms:
        raise ValueError("SPINDLE_OPERATING_POINTS_REQUIRED")
    normalized_rpms = tuple(
        _positive_finite(rpm, code="SPINDLE_OPERATING_RPM_INVALID")
        for rpm in requested_rpms
    )
    if any(current >= following for current, following in zip(normalized_rpms, normalized_rpms[1:])):
        raise ValueError("SPINDLE_OPERATING_POINT_RPM_ORDER_INVALID")
    if not any(math.isclose(rpm, source.spindle_rpm_reference, abs_tol=5e-9) for rpm in normalized_rpms):
        raise ValueError("SPINDLE_REFERENCE_RPM_NOT_AUDITED")

    operating_points = []
    for rpm in normalized_rpms:
        if rpm < curve[0].spindle_rpm or rpm > curve[-1].spindle_rpm:
            raise ValueError("SPINDLE_OPERATING_POINT_OUTSIDE_CURVE")
        lower, upper = next(
            (first, second)
            for first, second in zip(curve, curve[1:])
            if first.spindle_rpm <= rpm <= second.spindle_rpm
        )
        fraction = (rpm - lower.spindle_rpm) / (upper.spindle_rpm - lower.spindle_rpm)
        available_torque_nm = lower.available_torque_nm + fraction * (
            upper.available_torque_nm - lower.available_torque_nm
        )
        angular_factor = 2.0 * math.pi * rpm / 60_000.0
        available_power_kw = available_torque_nm * angular_factor
        required_power_kw = source.pc_cutting_kw
        required_torque_nm = required_power_kw / angular_factor
        power_margin_kw = available_power_kw - required_power_kw
        torque_margin_nm = available_torque_nm - required_torque_nm
        status: Literal[
            "WITHIN_POWER_TORQUE_ENVELOPE",
            "POWER_TORQUE_ENVELOPE_EXCEEDED",
        ] = (
            "WITHIN_POWER_TORQUE_ENVELOPE"
            if power_margin_kw >= 0 and torque_margin_nm >= 0
            else "POWER_TORQUE_ENVELOPE_EXCEEDED"
        )
        operating_points.append(
            SpindlePowerTorqueOperatingPoint(
                spindle_rpm=rpm,
                required_cutting_power_kw=required_power_kw,
                required_torque_nm=required_torque_nm,
                available_power_kw=available_power_kw,
                available_torque_nm=available_torque_nm,
                power_margin_kw=power_margin_kw,
                power_margin_percent=(power_margin_kw / available_power_kw) * 100.0,
                torque_margin_nm=torque_margin_nm,
                status=status,
            )
        )

    audit_status: Literal[
        "POWER_TORQUE_ENVELOPE_COMPLIANT",
        "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING",
    ] = (
        "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING"
        if any(point.status == "POWER_TORQUE_ENVELOPE_EXCEEDED" for point in operating_points)
        else "POWER_TORQUE_ENVELOPE_COMPLIANT"
    )
    return SpindlePowerTorqueEnvelopeAuditPayload(
        source_power_force_audit=source,
        spindle_rpm_min=curve[0].spindle_rpm,
        spindle_rpm_max=curve[-1].spindle_rpm,
        curve_points=curve,
        operating_points=tuple(operating_points),
        audit_status=audit_status,
    )


__all__ = (
    "audit_spindle_power_torque_envelope",
    "declared_spindle_curve",
)
