import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import PartElasticDeflectionAuditPayload
from app.modules.cnc.services.part_deflection_auditor import (
    PartDeflectionAuditError,
    audit_part_elastic_deflection,
    material_young_modulus_mpa,
)


def test_cylindrical_cantilever_deflection_matches_closed_form_solution() -> None:
    audit = audit_part_elastic_deflection(
        part_unsupported_length_mm=100.0,
        minimum_diameter_mm=40.0,
        radial_cutting_force_n=500.0,
        young_modulus_mpa=210_000.0,
    )

    expected_area = math.pi * 40.0**4 / 64.0
    expected_deflection_um = 500.0 * 100.0**3 / (3.0 * 210_000.0 * expected_area) * 1_000.0
    assert audit.second_moment_area_mm4 == pytest.approx(expected_area)
    assert audit.max_deflection_um == pytest.approx(expected_deflection_um)
    assert audit.calculated_stiffness_n_per_mm == pytest.approx(500.0 / (expected_deflection_um / 1_000.0))
    assert audit.deflection_status == "ELASTIC_DEFLECTION_COMPLIANT"
    assert audit.theoretical is True
    assert audit.physical is False
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False


def test_smaller_diameter_and_longer_overhang_raise_deflection_by_expected_ratio() -> None:
    baseline = audit_part_elastic_deflection(
        part_unsupported_length_mm=50.0,
        minimum_diameter_mm=40.0,
        radial_cutting_force_n=100.0,
        young_modulus_mpa=210_000.0,
    )
    flexible = audit_part_elastic_deflection(
        part_unsupported_length_mm=100.0,
        minimum_diameter_mm=20.0,
        radial_cutting_force_n=100.0,
        young_modulus_mpa=210_000.0,
    )

    assert flexible.max_deflection_um / baseline.max_deflection_um == pytest.approx(128.0)


def test_deflection_above_radial_tolerance_emits_warning() -> None:
    audit = audit_part_elastic_deflection(
        part_unsupported_length_mm=200.0,
        minimum_diameter_mm=10.0,
        radial_cutting_force_n=1_000.0,
        young_modulus_mpa=69_000.0,
        radial_tolerance_mm=0.02,
    )

    assert audit.max_deflection_um > 20.0
    assert audit.deflection_status == "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING"


@pytest.mark.parametrize(
    "updates",
    (
        {"part_unsupported_length_mm": 0.0},
        {"minimum_diameter_mm": -1.0},
        {"radial_cutting_force_n": 0.0},
        {"young_modulus_mpa": float("nan")},
        {"radial_tolerance_mm": 0.0},
    ),
)
def test_nonphysical_or_missing_beam_inputs_fail_closed(updates: dict[str, float]) -> None:
    values = {
        "part_unsupported_length_mm": 100.0,
        "minimum_diameter_mm": 40.0,
        "radial_cutting_force_n": 500.0,
        "young_modulus_mpa": 210_000.0,
        "radial_tolerance_mm": 0.02,
    }
    values.update(updates)

    with pytest.raises(PartDeflectionAuditError, match="PART_DEFLECTION_INPUT_INVALID"):
        audit_part_elastic_deflection(**values)


def test_payload_rejects_tampered_deflection_and_status() -> None:
    audit = audit_part_elastic_deflection(
        part_unsupported_length_mm=100.0,
        minimum_diameter_mm=40.0,
        radial_cutting_force_n=500.0,
        young_modulus_mpa=210_000.0,
    )
    body = audit.model_dump()
    body["max_deflection_um"] *= 2.0
    body["deflection_status"] = "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING"

    with pytest.raises(ValidationError, match="PART_DEFLECTION_VALUE_INCONSISTENT"):
        PartElasticDeflectionAuditPayload.model_validate(body)


def test_material_modulus_profile_is_explicit_and_unknown_profiles_fail_closed() -> None:
    assert material_young_modulus_mpa("ABNT_1045") == 210_000.0
    assert material_young_modulus_mpa("ALUMINUM_6061_T6") == 69_000.0
    with pytest.raises(
        PartDeflectionAuditError,
        match="PART_DEFLECTION_MATERIAL_PROFILE_INVALID",
    ):
        material_young_modulus_mpa("UNKNOWN")
