import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import JawClampingPressureAuditPayload
from app.modules.cnc.services.jaw_contact_pressure_auditor import (
    JawContactPressureAuditError,
    audit_jaw_contact_pressure,
    material_yield_strength_mpa,
)
from app.modules.cnc.services.workholding_auditor import audit_workholding_clamping


def _workholding(*, static_force_per_jaw_n: float = 15_000.0):
    return audit_workholding_clamping(
        static_clamping_force_per_jaw_n=static_force_per_jaw_n,
        jaw_mass_kg=0.25,
        center_of_mass_radius_mm=40.0,
        operating_rpm=1_000.0,
        maximum_declared_rpm=6_000.0,
        axial_cutting_force_n=1_000.0,
        friction_coefficient=0.30,
        required_safety_factor=2.0,
    )


def _audit(
    *,
    material_profile: str = "ABNT_1045",
    jaw_width_mm: float = 20.0,
    effective_contact_length_mm: float = 30.0,
    static_force_per_jaw_n: float = 15_000.0,
):
    return audit_jaw_contact_pressure(
        _workholding(static_force_per_jaw_n=static_force_per_jaw_n),
        material_profile=material_profile,
        jaw_width_mm=jaw_width_mm,
        effective_contact_length_mm=effective_contact_length_mm,
    )


def test_pressure_and_yield_ratio_are_exactly_derived_from_route_27() -> None:
    source = _workholding()
    audit = audit_jaw_contact_pressure(
        source,
        material_profile="ABNT_1045",
        jaw_width_mm=20.0,
        effective_contact_length_mm=30.0,
    )

    expected_area = 600.0
    expected_pressure = source.dynamic_clamping_force_total_n / 3.0 / expected_area
    expected_minimum = (
        source.required_safety_factor
        * source.axial_cutting_force_n
        / source.friction_coefficient
        / 3.0
        / expected_area
    )
    assert audit.source_workholding_clamping_audit == source
    assert audit.contact_area_mm2 == pytest.approx(expected_area)
    assert audit.mean_contact_pressure_mpa == pytest.approx(expected_pressure)
    assert audit.minimum_retention_pressure_mpa == pytest.approx(expected_minimum)
    assert audit.material_yield_strength_mpa == pytest.approx(350.0)
    assert audit.pressure_ratio_percent == pytest.approx(expected_pressure / 350.0 * 100.0)
    assert audit.clamping_pressure_status == "CLAMPING_PRESSURE_COMPLIANT"
    assert audit.theoretical is True
    assert audit.physical is False
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert audit.automatic_chuck_pressure_control_authorized is False
    assert JawClampingPressureAuditPayload.model_validate_json(audit.model_dump_json()) == audit


@pytest.mark.parametrize("material_profile", ["ALUMINUM_6061_T6", "AISI_1020"])
def test_high_clamping_pressure_warns_for_aluminum_and_annealed_steel(
    material_profile: str,
) -> None:
    audit = _audit(
        material_profile=material_profile,
        jaw_width_mm=10.0,
        effective_contact_length_mm=10.0,
        static_force_per_jaw_n=50_000.0,
    )

    assert audit.mean_contact_pressure_mpa > 0.6 * audit.material_yield_strength_mpa
    assert audit.clamping_pressure_status == "JAW_SURFACE_INDENTATION_RISK_WARNING"


def test_low_dynamic_pressure_warns_for_insufficient_static_retention() -> None:
    audit = _audit(static_force_per_jaw_n=1_000.0)

    assert audit.mean_contact_pressure_mpa < audit.minimum_retention_pressure_mpa
    assert audit.clamping_pressure_status == "INSUFFICIENT_CLAMPING_PRESSURE_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("jaw_width_mm", None, "JAW_CONTACT_WIDTH_INVALID"),
        ("jaw_width_mm", 0.0, "JAW_CONTACT_WIDTH_INVALID"),
        (
            "effective_contact_length_mm",
            -1.0,
            "JAW_CONTACT_EFFECTIVE_LENGTH_INVALID",
        ),
    ],
)
def test_null_or_negative_contact_dimensions_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    values: dict[str, object] = {
        "workholding_audit": _workholding(),
        "material_profile": "ABNT_1045",
        "jaw_width_mm": 20.0,
        "effective_contact_length_mm": 30.0,
    }
    values[field] = value
    with pytest.raises(JawContactPressureAuditError, match=code):
        audit_jaw_contact_pressure(**values)  # type: ignore[arg-type]


def test_negative_route_27_dynamic_force_fails_closed() -> None:
    invalid_source = _workholding().model_copy(update={"dynamic_clamping_force_total_n": -1.0})
    with pytest.raises(
        JawContactPressureAuditError,
        match="JAW_CONTACT_WORKHOLDING_AUDIT_INVALID",
    ):
        audit_jaw_contact_pressure(
            invalid_source,
            material_profile="ABNT_1045",
            jaw_width_mm=20.0,
            effective_contact_length_mm=30.0,
        )


@pytest.mark.parametrize("area", [None, -1.0])
def test_contract_rejects_null_or_negative_contact_area(area: object) -> None:
    body = _audit().model_dump()
    body["contact_area_mm2"] = area
    with pytest.raises(ValidationError):
        JawClampingPressureAuditPayload.model_validate(body)


def test_unknown_material_fails_closed() -> None:
    with pytest.raises(
        JawContactPressureAuditError,
        match="JAW_CONTACT_MATERIAL_PROFILE_INVALID",
    ):
        _audit(material_profile="UNLISTED")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("contact_area_mm2", 1.0, "JAW_CONTACT_AREA_INCONSISTENT"),
        ("mean_contact_pressure_mpa", 1.0, "JAW_CONTACT_MEAN_PRESSURE_INCONSISTENT"),
        ("material_yield_strength_mpa", 1.0, "JAW_CONTACT_YIELD_STRENGTH_INCONSISTENT"),
        ("pressure_ratio_percent", 1.0, "JAW_CONTACT_PRESSURE_RATIO_INCONSISTENT"),
        (
            "clamping_pressure_status",
            "JAW_SURFACE_INDENTATION_RISK_WARNING",
            "JAW_CONTACT_PRESSURE_STATUS_INCONSISTENT",
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
        JawClampingPressureAuditPayload.model_validate(body)


def test_material_yield_table_is_fixed() -> None:
    assert material_yield_strength_mpa("AISI_1020") == 250.0
    assert material_yield_strength_mpa("ABNT_1045") == 350.0
    assert material_yield_strength_mpa("ALUMINUM_6061_T6") == 276.0
