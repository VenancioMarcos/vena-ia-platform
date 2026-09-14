import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import WorkholdingClampingAuditPayload
from app.modules.cnc.services.workholding_auditor import (
    WorkholdingAuditError,
    audit_workholding_clamping,
)


def _audit(*, rpm: float, static_force: float = 5_000.0):
    return audit_workholding_clamping(
        static_clamping_force_per_jaw_n=static_force,
        jaw_mass_kg=0.5,
        center_of_mass_radius_mm=50.0,
        operating_rpm=rpm,
        maximum_declared_rpm=6_000.0,
        axial_cutting_force_n=1_000.0,
        friction_coefficient=0.30,
        required_safety_factor=2.0,
    )


def test_centrifugal_loss_is_deterministic_and_quadratic_with_rpm() -> None:
    low = _audit(rpm=1_000.0)
    high = _audit(rpm=4_000.0)

    assert high.centrifugal_force_per_jaw_n == pytest.approx(
        low.centrifugal_force_per_jaw_n * 16.0
    )
    assert high.total_centrifugal_loss_n == pytest.approx(
        low.total_centrifugal_loss_n * 16.0
    )
    assert high.dynamic_clamping_force_total_n < low.dynamic_clamping_force_total_n
    assert low.clamping_status == "DYNAMIC_CLAMPING_SAFE"
    assert high.clamping_status == "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING"
    assert high.clamping_safety_factor < 2.0
    assert high.physical_use_authorized is False
    assert high.automatic_chuck_control_authorized is False
    assert WorkholdingClampingAuditPayload.model_validate_json(high.model_dump_json()) == high


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"jaw_mass_kg": -1.0}, "WORKHOLDING_JAW_MASS_INVALID"),
        ({"center_of_mass_radius_mm": 0.0}, "WORKHOLDING_CENTER_OF_MASS_RADIUS_INVALID"),
        ({"operating_rpm": 6_001.0}, "WORKHOLDING_OPERATING_RPM_EXCEEDS_DECLARED_LIMIT"),
        ({"friction_coefficient": 1.01}, "WORKHOLDING_FRICTION_OUTSIDE_PHYSICAL_LIMITS"),
        ({"required_safety_factor": 1.99}, "WORKHOLDING_REQUIRED_SAFETY_FACTOR_INVALID"),
    ],
)
def test_nonphysical_inputs_fail_closed(updates: dict[str, float], code: str) -> None:
    values = {
        "static_clamping_force_per_jaw_n": 5_000.0,
        "jaw_mass_kg": 0.5,
        "center_of_mass_radius_mm": 50.0,
        "operating_rpm": 1_000.0,
        "maximum_declared_rpm": 6_000.0,
        "axial_cutting_force_n": 1_000.0,
        "friction_coefficient": 0.30,
        "required_safety_factor": 2.0,
    }
    values.update(updates)
    with pytest.raises(WorkholdingAuditError, match=code):
        audit_workholding_clamping(**values)


def test_total_loss_of_grip_fails_closed() -> None:
    with pytest.raises(WorkholdingAuditError, match="WORKHOLDING_TOTAL_CLAMPING_LOSS"):
        _audit(rpm=5_000.0, static_force=1_000.0)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("total_centrifugal_loss_n", 1.0, "WORKHOLDING_CENTRIFUGAL_LOSS_INCONSISTENT"),
        (
            "dynamic_clamping_force_total_n",
            1.0,
            "WORKHOLDING_DYNAMIC_CLAMPING_FORCE_INCONSISTENT",
        ),
        ("clamping_safety_factor", 99.0, "WORKHOLDING_SAFETY_FACTOR_INCONSISTENT"),
        (
            "clamping_status",
            "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING",
            "WORKHOLDING_CLAMPING_STATUS_INCONSISTENT",
        ),
    ],
)
def test_replayed_contract_rejects_tampered_derived_values(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _audit(rpm=1_000.0).model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        WorkholdingClampingAuditPayload.model_validate(body)


def test_contract_rejects_authority_promotion() -> None:
    body = _audit(rpm=1_000.0).model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        WorkholdingClampingAuditPayload.model_validate(body)

    body = _audit(rpm=1_000.0).model_dump()
    body["automatic_chuck_control_authorized"] = True
    with pytest.raises(ValidationError):
        WorkholdingClampingAuditPayload.model_validate(body)
