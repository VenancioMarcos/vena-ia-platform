import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import TailstockThrustAuditPayload
from app.modules.cnc.services.part_deflection_auditor import audit_part_elastic_deflection
from app.modules.cnc.services.tailstock_auditor import (
    TailstockAuditError,
    audit_tailstock_thrust_deflection,
)


def _audit(*, tailstock_force_n: float = 5_000.0):
    return audit_tailstock_thrust_deflection(
        tailstock_force_n=tailstock_force_n,
        total_supported_length_mm=200.0,
        minimum_diameter_mm=20.0,
        cutting_load_position_mm=100.0,
        radial_cutting_force_n=1_000.0,
        young_modulus_mpa=210_000.0,
        engagement_z_coordinate_mm=0.0,
        effective_length_factor=0.7,
    )


def test_fixed_pinned_support_substantially_reduces_cantilever_deflection() -> None:
    supported = _audit()
    cantilever = audit_part_elastic_deflection(
        part_unsupported_length_mm=200.0,
        minimum_diameter_mm=20.0,
        radial_cutting_force_n=1_000.0,
        young_modulus_mpa=210_000.0,
        radial_tolerance_mm=10.0,
    )

    assert supported.max_supported_deflection_um == pytest.approx(
        cantilever.max_deflection_um / 16.0
    )
    assert supported.tailstock_status == "TAILSTOCK_SUPPORT_COMPLIANT"
    assert supported.physical_use_authorized is False
    assert supported.automatic_tailstock_control_authorized is False
    assert TailstockThrustAuditPayload.model_validate_json(
        supported.model_dump_json()
    ) == supported


def test_tailstock_preload_above_thirty_percent_of_euler_load_warns() -> None:
    reference = _audit()
    warning = _audit(tailstock_force_n=reference.warning_threshold_n * 1.01)

    assert warning.tailstock_force_n > warning.critical_buckling_load_n * 0.3
    assert warning.tailstock_status == "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING"


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"tailstock_force_n": -1.0}, "TAILSTOCK_FORCE_INVALID"),
        ({"total_supported_length_mm": 0.0}, "TAILSTOCK_SUPPORTED_LENGTH_INVALID"),
        ({"minimum_diameter_mm": 0.0}, "TAILSTOCK_DIAMETER_INVALID"),
        ({"cutting_load_position_mm": 200.0}, "TAILSTOCK_CUTTING_POSITION_OUTSIDE"),
        ({"radial_cutting_force_n": 0.0}, "TAILSTOCK_RADIAL_FORCE_INVALID"),
        ({"young_modulus_mpa": 0.0}, "TAILSTOCK_YOUNG_MODULUS_INVALID"),
        ({"engagement_z_coordinate_mm": None}, "TAILSTOCK_ENGAGEMENT_COORDINATE_REQUIRED"),
    ],
)
def test_nonphysical_or_missing_inputs_fail_closed(
    updates: dict[str, object],
    code: str,
) -> None:
    values: dict[str, object] = {
        "tailstock_force_n": 5_000.0,
        "total_supported_length_mm": 200.0,
        "minimum_diameter_mm": 20.0,
        "cutting_load_position_mm": 100.0,
        "radial_cutting_force_n": 1_000.0,
        "young_modulus_mpa": 210_000.0,
        "engagement_z_coordinate_mm": 0.0,
        "effective_length_factor": 0.7,
    }
    values.update(updates)
    with pytest.raises(TailstockAuditError, match=code):
        audit_tailstock_thrust_deflection(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("critical_buckling_load_n", 1.0, "TAILSTOCK_CRITICAL_BUCKLING_LOAD_INCONSISTENT"),
        ("max_supported_deflection_um", 1.0, "TAILSTOCK_DEFLECTION_INCONSISTENT"),
        ("warning_threshold_n", 1.0, "TAILSTOCK_WARNING_THRESHOLD_INCONSISTENT"),
        (
            "tailstock_status",
            "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING",
            "TAILSTOCK_STATUS_INCONSISTENT",
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
        TailstockThrustAuditPayload.model_validate(body)


def test_contract_rejects_authority_promotion() -> None:
    body = _audit().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        TailstockThrustAuditPayload.model_validate(body)

    body = _audit().model_dump()
    body["automatic_tailstock_control_authorized"] = True
    with pytest.raises(ValidationError):
        TailstockThrustAuditPayload.model_validate(body)
