import math

import pytest
from pydantic import ValidationError

from app.modules.cam.enums import CompensationType, ToolOrientation, TurningOperationType
from app.modules.cam.schemas import (
    CuttingParameters,
    RzPoint,
    TurningBoundingBox,
    TurningStrategyPlanRequest,
    TurningStrategyPlanResponse,
    TurningToolParams,
)
from app.modules.cam.services.strategy_engine import (
    TurningStrategyValidationError,
    plan_turning_strategy,
)


def _request(
    *,
    operation_type: TurningOperationType = TurningOperationType.ROUGH_TURNING,
    depth_of_cut_mm: float = 2.0,
    profile_data: tuple[RzPoint, ...] | None = None,
    tip_radius_mm: float = 0.8,
    finish_allowance_mm: float = 0.0,
    cutting_edge_angle_deg: float = 95.0,
    cutting_edge_length_mm: float = 12.0,
) -> TurningStrategyPlanRequest:
    return TurningStrategyPlanRequest(
        operation_type=operation_type,
        profile_data=profile_data
        or (
            RzPoint(r_mm=0.0, z_mm=0.0),
            RzPoint(r_mm=10.0, z_mm=0.0),
            RzPoint(r_mm=10.0, z_mm=-20.0),
            RzPoint(r_mm=0.0, z_mm=-20.0),
        ),
        bounding_box=TurningBoundingBox(
            max_radius_mm=10.0,
            min_z_mm=-20.0,
            max_z_mm=0.0,
            total_z_length_mm=20.0,
        ),
        linear_tolerance_mm=0.001,
        material_reference="AISI 1020 reference only",
        stock_radius_mm=14.0,
        stock_front_z_mm=2.0,
        target_front_z_mm=0.0,
        finish_allowance_mm=finish_allowance_mm,
        tool=TurningToolParams(
            tip_radius_mm=tip_radius_mm,
            cutting_edge_angle_deg=cutting_edge_angle_deg,
            cutting_edge_length_mm=cutting_edge_length_mm,
            orientation=ToolOrientation.RIGHT_HAND,
            compensation=CompensationType.NONE,
        ),
        cutting_parameters=CuttingParameters(
            vc_m_per_min=180.0,
            feed_mm_per_rev=0.2,
            depth_of_cut_mm=depth_of_cut_mm,
        ),
        review_status="PROFILE_AVAILABLE_REQUIRES_REVIEW",
    )


def test_plans_deterministic_linear_roughing_for_valid_axisymmetric_profile() -> None:
    request = _request()

    result = plan_turning_strategy(request)

    assert result == plan_turning_strategy(request)
    assert result.status == "PLANNED_REQUIRES_REVIEW"
    assert result.operation_type == TurningOperationType.ROUGH_TURNING
    assert [item.coordinates_rz_mm[1].r_mm for item in result.passes] == [12.0, 10.0]
    assert math.isclose(
        result.material_removal_volume_mm3,
        math.pi * (14.0**2 - 10.0**2) * 20.0,
    )
    assert result.executable_output is False
    assert result.physical_use_authorized is False
    assert result.g9_status == "PENDING_AUTHORITATIVE_REVIEW"


def test_plans_initial_facing_from_stock_z_to_target_z() -> None:
    result = plan_turning_strategy(
        _request(operation_type=TurningOperationType.FACING, depth_of_cut_mm=0.75)
    )

    assert len(result.passes) == 3
    assert [item.coordinates_rz_mm[0].z_mm for item in result.passes] == [1.25, 0.5, 0.0]
    assert math.isclose(result.material_removal_volume_mm3, math.pi * 14.0**2 * 2.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (("depth_of_cut_mm", 0.0), ("depth_of_cut_mm", -0.1), ("feed_mm_per_rev", 0.0)),
)
def test_rejects_invalid_cutting_parameters(field: str, value: float) -> None:
    payload = {
        "vc_m_per_min": 180.0,
        "feed_mm_per_rev": 0.2,
        "depth_of_cut_mm": 2.0,
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        CuttingParameters.model_validate(payload)


def test_contracts_are_strict_round_trip_and_forbid_physical_forgery() -> None:
    result = plan_turning_strategy(_request())

    assert TurningStrategyPlanResponse.model_validate_json(result.model_dump_json()) == result
    with pytest.raises(ValidationError):
        TurningStrategyPlanRequest.model_validate(
            {**_request().model_dump(), "stock_radius_mm": "14.0"}
        )
    with pytest.raises(ValidationError):
        TurningStrategyPlanResponse.model_validate(
            {**result.model_dump(), "physical_use_authorized": True}
        )


def test_engine_rejects_profile_outside_declared_bounding_box() -> None:
    request = _request().model_copy(
        update={
            "profile_data": (
                RzPoint(r_mm=0.0, z_mm=0.0),
                RzPoint(r_mm=10.1, z_mm=0.0),
                RzPoint(r_mm=10.0, z_mm=-20.0),
            )
        }
    )

    with pytest.raises(
        TurningStrategyValidationError, match="PROFILE_OUTSIDE_DECLARED_BOUNDING_BOX"
    ):
        plan_turning_strategy(request)


def test_plans_continuous_finishing_with_nose_radius_and_allowance() -> None:
    result = plan_turning_strategy(
        _request(
            operation_type=TurningOperationType.FINISHING,
            finish_allowance_mm=0.2,
        )
    )

    assert result.operation_type == TurningOperationType.FINISHING
    assert len(result.passes) == 1
    assert result.passes[0].operation_type == TurningOperationType.FINISHING
    assert result.passes[0].coordinates_rz_mm == (
        RzPoint(r_mm=11.0, z_mm=0.0),
        RzPoint(r_mm=11.0, z_mm=-20.0),
    )
    assert result.material_removal_volume_mm3 == 0.0
    assert "TOOL_CENTER_PATH_INCLUDES_2D_NOSE_RADIUS_COMPENSATION" in result.warnings


def test_plans_finishing_for_sampled_curved_profile_deterministically() -> None:
    profile = (
        RzPoint(r_mm=0.0, z_mm=0.0),
        RzPoint(r_mm=10.0, z_mm=0.0),
        RzPoint(r_mm=10.4, z_mm=-4.0),
        RzPoint(r_mm=11.0, z_mm=-10.0),
        RzPoint(r_mm=11.4, z_mm=-16.0),
        RzPoint(r_mm=11.5, z_mm=-20.0),
        RzPoint(r_mm=0.0, z_mm=-20.0),
    )
    request = _request(
        operation_type=TurningOperationType.FINISHING,
        profile_data=profile,
    ).model_copy(
        update={
            "bounding_box": TurningBoundingBox(
                max_radius_mm=11.5,
                min_z_mm=-20.0,
                max_z_mm=0.0,
                total_z_length_mm=20.0,
            )
        }
    )

    result = plan_turning_strategy(request)

    assert result == plan_turning_strategy(request)
    assert len(result.passes[0].coordinates_rz_mm) == 5
    assert all(
        compensated.r_mm > nominal.r_mm
        for compensated, nominal in zip(
            result.passes[0].coordinates_rz_mm,
            profile[1:-1],
        )
    )


def test_finishing_rejects_tool_nose_larger_than_concave_profile_radius() -> None:
    profile = (
        RzPoint(r_mm=0.0, z_mm=0.0),
        RzPoint(r_mm=10.0, z_mm=0.0),
        RzPoint(r_mm=10.0, z_mm=-0.2),
        RzPoint(r_mm=9.5, z_mm=-0.5),
        RzPoint(r_mm=9.0, z_mm=-1.0),
        RzPoint(r_mm=9.5, z_mm=-1.5),
        RzPoint(r_mm=10.0, z_mm=-2.0),
        RzPoint(r_mm=10.0, z_mm=-20.0),
        RzPoint(r_mm=0.0, z_mm=-20.0),
    )
    with pytest.raises(
        TurningStrategyValidationError,
        match="TOOL_GEOMETRY_UNDERCUT_COLLISION",
    ):
        plan_turning_strategy(
            _request(
                operation_type=TurningOperationType.FINISHING,
                profile_data=profile,
                tip_radius_mm=2.0,
            )
        )


def test_finishing_rejects_insufficient_angle_projected_edge_reach() -> None:
    with pytest.raises(
        TurningStrategyValidationError,
        match="TOOL_GEOMETRY_UNDERCUT_COLLISION",
    ):
        plan_turning_strategy(
            _request(
                operation_type=TurningOperationType.FINISHING,
                tip_radius_mm=0.8,
                finish_allowance_mm=0.2,
                cutting_edge_angle_deg=5.0,
                cutting_edge_length_mm=2.0,
            )
        )


def test_grooving_remains_fail_closed() -> None:
    with pytest.raises(
        TurningStrategyValidationError, match="OPERATION_NOT_IMPLEMENTED_IN_FOUNDATION"
    ):
        plan_turning_strategy(_request(operation_type=TurningOperationType.GROOVING))
