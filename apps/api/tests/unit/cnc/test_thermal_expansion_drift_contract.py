import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ThermalExpansionDriftAuditPayload
from app.modules.cnc.services.thermal_expansion_auditor import audit_thermal_expansion_drift


def _audit(**updates: float | str) -> ThermalExpansionDriftAuditPayload:
    values: dict[str, float | str] = {
        "material_reference": "Aço ABNT 1045",
        "workpiece_mean_temperature_c": 40.0,
        "spindle_mean_temperature_c": 30.0,
        "workpiece_length_mm": 200.0,
        "workpiece_diameter_mm": 50.0,
        "spindle_effective_length_mm": 150.0,
        "z_axis_tolerance_um": 100.0,
        "x_axis_tolerance_um": 100.0,
    }
    values.update(updates)
    return audit_thermal_expansion_drift(**values)  # type: ignore[arg-type]


def test_carbon_steel_expansion_and_contract_replay() -> None:
    audit = _audit()
    assert audit.linear_expansion_coefficient_per_c == 12e-6
    assert audit.workpiece_z_expansion_um == pytest.approx(48.0)
    assert audit.workpiece_x_expansion_um == pytest.approx(6.0)
    assert audit.spindle_z_drift_um == pytest.approx(18.0)
    assert audit.total_z_axis_drift_um == pytest.approx(66.0)
    assert audit.total_x_axis_drift_um == pytest.approx(6.0)
    assert audit.audit_status == "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE"
    assert ThermalExpansionDriftAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_aluminum_6061_uses_tabulated_coefficient() -> None:
    audit = _audit(material_reference="Alumínio 6061-T6")
    assert audit.linear_expansion_coefficient_per_c == 23e-6
    assert audit.workpiece_z_expansion_um == pytest.approx(92.0)
    assert audit.workpiece_x_expansion_um == pytest.approx(11.5)


def test_reference_temperature_produces_zero_drift() -> None:
    audit = _audit(workpiece_mean_temperature_c=20.0, spindle_mean_temperature_c=20.0)
    assert audit.total_z_axis_drift_um == 0
    assert audit.total_x_axis_drift_um == 0


def test_overheating_produces_warning() -> None:
    audit = _audit(workpiece_mean_temperature_c=100.0, z_axis_tolerance_um=50.0)
    assert audit.audit_status == "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING"


@pytest.mark.parametrize("temperature", [-41.0, 301.0, math.nan, math.inf])
def test_non_physical_temperature_fails_closed(temperature: float) -> None:
    with pytest.raises(ValueError, match="THERMAL_WORKPIECE_TEMPERATURE_INVALID"):
        _audit(workpiece_mean_temperature_c=temperature)


def test_unknown_material_and_incoherent_delta_fail_closed() -> None:
    with pytest.raises(ValueError, match="THERMAL_MATERIAL_UNSUPPORTED"):
        _audit(material_reference="UNLISTED")
    with pytest.raises(ValueError, match="THERMAL_DELTA_TEMPERATURE_INCONSISTENT"):
        _audit(spindle_mean_temperature_c=19.0)


def test_derived_drift_cannot_be_adulterated() -> None:
    body = _audit().model_dump()
    body["total_z_axis_drift_um"] += 1.0
    with pytest.raises(ValidationError, match="THERMAL_TOTAL_Z_DRIFT_INCONSISTENT"):
        ThermalExpansionDriftAuditPayload.model_validate(body)
