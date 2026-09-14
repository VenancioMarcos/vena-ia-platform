import pytest
from pydantic import ValidationError

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import MachiningPass, RzPoint, TurningStrategyPlanResponse
from app.modules.cnc.schemas import MachiningResidualStockAuditPayload
from app.modules.cnc.services.residual_stock_auditor import (
    ResidualStockAuditError,
    audit_residual_stock,
)


def _profile() -> tuple[RzPoint, ...]:
    return (
        RzPoint(r_mm=0.0, z_mm=0.0),
        RzPoint(r_mm=10.0, z_mm=0.0),
        RzPoint(r_mm=10.0, z_mm=-20.0),
        RzPoint(r_mm=0.0, z_mm=-20.0),
    )


def _plan(radius_mm: float) -> TurningStrategyPlanResponse:
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.ROUGH_TURNING,
        passes=(
            MachiningPass(
                sequence=1,
                operation_type=TurningOperationType.ROUGH_TURNING,
                coordinates_rz_mm=(
                    RzPoint(r_mm=12.0, z_mm=0.0),
                    RzPoint(r_mm=radius_mm, z_mm=0.0),
                    RzPoint(r_mm=radius_mm, z_mm=-20.0),
                    RzPoint(r_mm=12.0, z_mm=-20.0),
                ),
                estimated_removed_volume_mm3=100.0,
            ),
        ),
        material_removal_volume_mm3=100.0,
        warnings=("ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW",),
    )


def _audit(radius_mm: float) -> MachiningResidualStockAuditPayload:
    return audit_residual_stock(
        source_plan_id="plan-residual-001",
        cam_plan=_plan(radius_mm),
        nominal_profile=_profile(),
        stock_radius_mm=12.0,
        finish_allowance_nominal_mm=0.0,
        linear_tolerance_mm=0.001,
        tool_cutting_edge_length_mm=12.0,
    )


def test_uniform_residual_profile_is_within_nominal_allowance_tolerance() -> None:
    audit = _audit(10.02)

    assert audit.status == "UNIFORM_ALLOWANCE_COMPLIANT"
    assert audit.min_residual_stock_mm == pytest.approx(0.02)
    assert audit.max_residual_stock_mm == pytest.approx(0.02)
    assert audit.average_stock_allowance_mm == pytest.approx(0.02)
    assert audit.gouging_detected is False
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False


def test_any_negative_residual_detects_critical_gouging_fail_closed() -> None:
    audit = _audit(9.99)

    assert audit.status == "CRITICAL_GOUGING_VIOLATION"
    assert audit.min_residual_stock_mm == pytest.approx(-0.01)
    assert audit.gouging_detected is True
    assert audit.safety_flags.executable_output is False


def test_excess_unmachined_stock_overloads_finish_pass() -> None:
    audit = _audit(10.2)

    assert audit.status == "EXCESS_MATERIAL_DETECTED"
    assert audit.max_residual_stock_mm == pytest.approx(0.2)
    assert audit.gouging_detected is False


def test_unmachined_step_beyond_tool_edge_length_is_rejected() -> None:
    profile = (
        RzPoint(r_mm=0.0, z_mm=0.0),
        RzPoint(r_mm=5.0, z_mm=0.0),
        RzPoint(r_mm=5.0, z_mm=-5.0),
        RzPoint(r_mm=20.0, z_mm=-5.0),
        RzPoint(r_mm=20.0, z_mm=-10.0),
        RzPoint(r_mm=0.0, z_mm=-10.0),
    )

    with pytest.raises(
        ResidualStockAuditError,
        match="RESIDUAL_STOCK_STEP_TOOL_INCOMPATIBLE",
    ):
        audit_residual_stock(
            source_plan_id="plan-step",
            cam_plan=_plan(10.0),
            nominal_profile=profile,
            stock_radius_mm=25.0,
            finish_allowance_nominal_mm=0.0,
            linear_tolerance_mm=0.001,
            tool_cutting_edge_length_mm=10.0,
        )


def test_payload_rejects_tampered_aggregate_and_status() -> None:
    body = _audit(10.02).model_dump()
    body["max_residual_stock_mm"] = 0.01
    body["status"] = "EXCESS_MATERIAL_DETECTED"

    with pytest.raises(ValidationError, match="RESIDUAL_STOCK_AGGREGATE_INCONSISTENT"):
        MachiningResidualStockAuditPayload.model_validate(body)
