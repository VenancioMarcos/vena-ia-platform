import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ThermalExpansionDriftAuditPayload


def _payload(
    *,
    material_profile: str = "ABNT_1045",
    alpha: float = 11.7e-6,
    workpiece_temperature_rise_c: float = 20.0,
    spindle_temperature_rise_c: float = 10.0,
    z_tolerance_um: float = 100.0,
    x_tolerance_um: float = 100.0,
) -> ThermalExpansionDriftAuditPayload:
    workpiece_z = alpha * 200.0 * workpiece_temperature_rise_c * 1_000
    workpiece_x = alpha * 50.0 * workpiece_temperature_rise_c * 1_000
    spindle_z = alpha * 150.0 * spindle_temperature_rise_c * 1_000
    spindle_x = alpha * 25.0 * spindle_temperature_rise_c * 1_000
    total_z = workpiece_z + spindle_z
    total_x = workpiece_x + spindle_x
    return ThermalExpansionDriftAuditPayload(
        material_profile=material_profile,
        linear_expansion_coefficient_per_c=alpha,
        workpiece_mean_temperature_rise_c=workpiece_temperature_rise_c,
        spindle_mean_temperature_rise_c=spindle_temperature_rise_c,
        workpiece_axial_reference_length_mm=200.0,
        workpiece_diameter_reference_mm=50.0,
        spindle_z_reference_length_mm=150.0,
        spindle_x_reference_length_mm=25.0,
        workpiece_z_expansion_um=workpiece_z,
        workpiece_x_expansion_um=workpiece_x,
        spindle_z_drift_um=spindle_z,
        spindle_x_drift_um=spindle_x,
        total_z_axis_drift_um=total_z,
        total_x_axis_drift_um=total_x,
        z_axis_tolerance_um=z_tolerance_um,
        x_axis_tolerance_um=x_tolerance_um,
        audit_status=(
            "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING"
            if total_z > z_tolerance_um or total_x > x_tolerance_um
            else "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE"
        ),
    )


def test_v2_contract_replays_deterministically_with_defensive_flags() -> None:
    audit = _payload()

    assert audit.schema_version == "vena-ia.cnc-thermal-expansion-drift-audit/v2"
    assert audit.total_z_axis_drift_um == pytest.approx(64.35)
    assert audit.total_x_axis_drift_um == pytest.approx(14.625)
    assert audit.audit_status == "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE"
    assert audit.theoretical is True
    assert audit.physical is False
    assert audit.physical_use_authorized is False
    assert audit.safety_flags.executable_output is False
    assert ThermalExpansionDriftAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_excessive_axis_drift_requires_warning_status() -> None:
    audit = _payload(z_tolerance_um=50.0)

    assert audit.audit_status == "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING"


def test_material_coefficient_is_fail_closed() -> None:
    with pytest.raises(ValidationError, match="THERMAL_EXPANSION_COEFFICIENT_INCONSISTENT"):
        _payload(material_profile="ALUMINUM_6061_T6", alpha=11.7e-6)


def test_derived_axis_drift_cannot_be_adulterated() -> None:
    body = _payload().model_dump()
    body["total_z_axis_drift_um"] += 1.0

    with pytest.raises(ValidationError, match="THERMAL_TOTAL_Z_DRIFT_INCONSISTENT"):
        ThermalExpansionDriftAuditPayload.model_validate(body)


@pytest.mark.parametrize("temperature", [-1.0, math.nan, math.inf])
def test_non_physical_temperature_is_rejected(temperature: float) -> None:
    with pytest.raises(ValidationError):
        _payload(workpiece_temperature_rise_c=temperature)
