import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import SpindleHarmonicDynamicsAuditPayload
from app.modules.cnc.services.harmonic_spindle_auditor import (
    HarmonicSpindleAuditError,
    audit_spindle_harmonic_dynamics,
    cylindrical_workpiece_mass_kg,
    material_density_kg_m3,
)


def _audit(**updates: float) -> SpindleHarmonicDynamicsAuditPayload:
    values = {
        "system_stiffness_n_per_m": 2_000_000.0,
        "effective_mass_kg": 2.0,
        "workpiece_mass_kg": 5.0,
        "mass_eccentricity_mm": 0.01,
        "operating_rpm": 3_000.0,
        "bearing_admissible_force_n": 10_000.0,
        "resonance_exclusion_percent": 15.0,
    }
    values.update(updates)
    return audit_spindle_harmonic_dynamics(**values)


@pytest.mark.parametrize(
    ("material_profile", "density"),
    [("AISI_1020", 7_850.0), ("ALUMINUM_6061_T6", 2_700.0)],
)
def test_calculates_deterministic_critical_speed_for_standard_cylinders(
    material_profile: str,
    density: float,
) -> None:
    diameter_mm = 40.0
    length_mm = 200.0
    mass = cylindrical_workpiece_mass_kg(
        diameter_mm=diameter_mm,
        length_mm=length_mm,
        density_kg_m3=material_density_kg_m3(material_profile),
    )
    expected_mass = density * math.pi * (diameter_mm / 2_000.0) ** 2 * (
        length_mm / 1_000.0
    )
    audit = audit_spindle_harmonic_dynamics(
        system_stiffness_n_per_m=2_000_000.0,
        effective_mass_kg=0.236 * mass,
        workpiece_mass_kg=mass,
        mass_eccentricity_mm=0.01,
        operating_rpm=3_000.0,
        bearing_admissible_force_n=10_000.0,
    )

    expected_rpm = math.sqrt(2_000_000.0 / (0.236 * expected_mass)) * 60 / (
        2 * math.pi
    )
    assert mass == pytest.approx(expected_mass)
    assert audit.first_critical_rpm == pytest.approx(expected_rpm)
    assert audit.physical_use_authorized is False
    assert audit.is_theoretical_model is True


def test_warns_inside_fifteen_percent_resonance_exclusion_band() -> None:
    reference = _audit()
    warning = _audit(operating_rpm=reference.first_critical_rpm * 1.149)

    assert warning.resonance_proximity_percent == pytest.approx(14.9)
    assert warning.dynamic_status == "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING"


def test_warns_when_unbalance_force_exceeds_bearing_limit() -> None:
    warning = _audit(mass_eccentricity_mm=10.0, bearing_admissible_force_n=1.0)

    assert warning.resonance_proximity_percent > 15
    assert warning.unbalance_force_n > warning.bearing_admissible_force_n
    assert warning.dynamic_status == "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING"


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"system_stiffness_n_per_m": 0.0}, "SPINDLE_HARMONIC_STIFFNESS_INVALID"),
        ({"effective_mass_kg": -1.0}, "SPINDLE_HARMONIC_EFFECTIVE_MASS_INVALID"),
        ({"workpiece_mass_kg": -1.0}, "SPINDLE_HARMONIC_WORKPIECE_MASS_INVALID"),
        ({"mass_eccentricity_mm": -0.01}, "SPINDLE_HARMONIC_ECCENTRICITY_INVALID"),
        ({"operating_rpm": 0.0}, "SPINDLE_HARMONIC_OPERATING_RPM_INVALID"),
        ({"operating_rpm": 100_001.0}, "SPINDLE_HARMONIC_OPERATING_RPM_INVALID"),
    ],
)
def test_nonphysical_inputs_fail_closed(updates: dict[str, float], code: str) -> None:
    with pytest.raises(HarmonicSpindleAuditError, match=code):
        _audit(**updates)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("first_critical_rpm", 1.0, "SPINDLE_HARMONIC_CRITICAL_RPM_INCONSISTENT"),
        ("unbalance_force_n", 1.0, "SPINDLE_HARMONIC_UNBALANCE_FORCE_INCONSISTENT"),
        (
            "dynamic_status",
            "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING",
            "SPINDLE_HARMONIC_STATUS_INCONSISTENT",
        ),
    ],
)
def test_contract_rejects_tampered_derived_values(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _audit().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        SpindleHarmonicDynamicsAuditPayload.model_validate(body)


def test_contract_rejects_authority_promotion() -> None:
    body = _audit().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        SpindleHarmonicDynamicsAuditPayload.model_validate(body)
