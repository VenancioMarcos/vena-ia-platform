import math
import sys
from pathlib import Path
from decimal import Inexact, ROUND_DOWN, getcontext, localcontext

import pytest
from pydantic import ValidationError

from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.profile_extractor import TurningDatum, extract_turning_profile
from app.modules.engineering.turning_planner import generate_turning_roughing_plan
from app.modules.engineering.turning_schemas import TurningStockCylinder
from app.modules.engineering.turning_quantization import (
    evaluate_diameter_quantization, evaluate_plan_diameter_quantization,
)
from app.modules.engineering.turning_toolpath_schemas import (
    SyntheticTurningParameters, TurningMotionType, TurningOperationPlan,
    TurningPlanQuantizationSummary, TurningToolpathMove, TurningToolpathPlan,
)


@pytest.mark.parametrize("radius,places,diameter", [
    (10.0, 3, 20.0), (12.34526, 3, 24.691), (12.34524, 3, 24.69),
    (0.0625, 2, 0.13), (1.25, 1, 2.5), (0.0, 6, 0.0),
])
def test_numeric_rounding_and_signed_deviation(radius: float, places: int, diameter: float) -> None:
    report = evaluate_diameter_quantization(radius, places)
    assert report.programmed_x_diameter_mm == diameter
    assert report.reconstructed_radius_mm == diameter / 2.0
    assert report.radial_deviation_mm == diameter / 2.0 - radius
    assert not report.is_boundary_safe and report.boundary_status == "NOT_EVALUATED"
    assert report.limitations == ("NUMERICAL_QUANTIZATION_CHECK_ONLY",)
    assert report == evaluate_diameter_quantization(radius, places)


@pytest.mark.parametrize("places", [-1, 0, 7, 1000000, True, 3.0, "3"])
def test_precision_is_strict_and_bounded(places: object) -> None:
    with pytest.raises(ValueError, match="decimal_places"):
        evaluate_diameter_quantization(10.0, places)  # type: ignore[arg-type]


@pytest.mark.parametrize("radius", [-1.0, math.nan, math.inf, -math.inf, True, 10, "10"])
def test_radius_contract_is_strict(radius: object) -> None:
    with pytest.raises(ValueError, match="radius"):
        evaluate_diameter_quantization(radius)  # type: ignore[arg-type]


def test_binary_tie_and_neighbors_are_explicit() -> None:
    # 0.125 is exactly representable; exact tie rounds upward to 0.13.
    assert evaluate_diameter_quantization(0.0625, 2).programmed_x_diameter_mm == 0.13
    assert evaluate_diameter_quantization(math.nextafter(0.0625, 0.0), 2).programmed_x_diameter_mm == 0.12
    assert evaluate_diameter_quantization(math.nextafter(0.0625, math.inf), 2).programmed_x_diameter_mm == 0.13


def test_context_independence_and_no_global_side_effect() -> None:
    expected = evaluate_diameter_quantization(12.34526)
    with localcontext() as context:
        context.prec = 2
        context.rounding = ROUND_DOWN
        context.Emax = 2
        context.Emin = -2
        context.traps[Inexact] = True
        context.clear_flags()
        before = (context.prec, context.rounding, context.Emax, context.Emin,
                  dict(context.traps), dict(context.flags))
        assert evaluate_diameter_quantization(12.34526) == expected
        assert (getcontext().prec, getcontext().rounding, getcontext().Emax, getcontext().Emin,
                dict(getcontext().traps), dict(getcontext().flags)) == before


def test_extremes_and_positive_value_lost_to_resolution_fail_closed() -> None:
    with pytest.raises(ValueError, match="overflow"):
        evaluate_diameter_quantization(sys.float_info.max)
    with pytest.raises(ValueError, match="lost"):
        evaluate_diameter_quantization(math.nextafter(0.0, math.inf), 6)
    with pytest.raises(ValueError, match="lost"):
        evaluate_diameter_quantization(1e-8, 6)
    result = evaluate_diameter_quantization(sys.float_info.max / 2, 6)
    assert result.programmed_x_diameter_mm == sys.float_info.max
    assert result.radial_deviation_mm == 0.0


def _numeric_plan(radii: tuple[float, ...]) -> TurningToolpathPlan:
    types = (TurningMotionType.RAPID, TurningMotionType.CUTTING, TurningMotionType.RETRACT)
    moves = tuple(TurningToolpathMove(
        start_point=(a, -float(i)), end_point=(b, -float(i+1)),
        motion_type=types[i % 3], feed_rate_type="MM_PER_REVOLUTION",
    ) for i, (a, b) in enumerate(zip(radii, radii[1:])))
    return TurningToolpathPlan(
        profile_id="synthetic-numeric", total_cutting_length_mm=math.fsum(
            math.dist(m.start_point, m.end_point) for m in moves
            if m.motion_type == TurningMotionType.CUTTING),
        operations=(TurningOperationPlan(operation_id="numeric", operation_type="FACING",
                    passes_count=sum(m.motion_type == TurningMotionType.CUTTING for m in moves),
                    moves=moves),),
    )


@pytest.mark.parametrize("name,diameter", [("cylinder_d50_l100", 60.0), ("stepped_d30_d60", 70.0)])
def test_real_planner_endpoint_aggregation(name: str, diameter: float) -> None:
    path = Path(__file__).parents[2] / "fixtures" / "cad" / "turning" / f"{name}.stp"
    shape, _ = OpenCascadeGeometryKernel()._load_step_shape(path.read_bytes())
    extraction = extract_turning_profile(
        shape, datum=TurningDatum(origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0)),
        source_unit="mm", linear_tolerance_mm=1e-6, angular_tolerance_rad=1e-7,
    )
    assert extraction.profile is not None
    plan = generate_turning_roughing_plan(
        extraction.profile,
        TurningStockCylinder(diameter_mm=diameter, length_mm=110.0, face_allowance_mm=3.0),
        SyntheticTurningParameters(axial_depth_mm=1.0, radial_depth_mm=2.0,
                                   axial_allowance_mm=0.5, radial_allowance_mm=0.50026,
                                   clearance_mm=1.0, feed_rate_type="MM_PER_REVOLUTION"),
    )
    original = plan.model_dump_json()
    report = evaluate_plan_diameter_quantization(plan)
    moves = [m for op in plan.operations for m in op.moves]
    assert {m.motion_type for m in moves} == set(TurningMotionType)
    assert report.evaluated_moves_count == len(moves)
    assert tuple(r.original_radius_mm for r in report.move_reports) == tuple(
        p[0] for m in moves for p in (m.start_point, m.end_point))
    assert report == evaluate_plan_diameter_quantization(plan)
    assert TurningPlanQuantizationSummary.model_validate_json(report.model_dump_json()) == report
    assert plan.model_dump_json() == original
    assert not report.is_boundary_safe and report.boundary_status == "NOT_EVALUATED"
    assert report.limitations == ("NUMERICAL_QUANTIZATION_AGGREGATE_ONLY",)


def test_aggregate_manual_extrema_and_repeated_endpoint_order() -> None:
    report = evaluate_plan_diameter_quantization(_numeric_plan((0.0625, 0.07, 0.061, 0.0625)), 2)
    expected = (0.065-0.0625, 0.0, 0.0, 0.06-0.061, 0.06-0.061, 0.065-0.0625)
    assert tuple(r.radial_deviation_mm for r in report.move_reports) == expected
    assert report.evaluated_moves_count == 3
    assert report.max_positive_radial_deviation_mm == 0.065-0.0625
    assert report.max_negative_radial_deviation_mm == 0.06-0.061


@pytest.mark.parametrize("radii", [(), (0.07, 0.07), (0.0625, 0.0625), (0.061, 0.061)])
def test_empty_and_one_sided_extrema(radii: tuple[float, ...]) -> None:
    result = evaluate_plan_diameter_quantization(_numeric_plan(radii), 2)
    assert result.max_positive_radial_deviation_mm >= 0.0
    assert result.max_negative_radial_deviation_mm <= 0.0
    if not radii:
        assert result.evaluated_moves_count == 0 and result.move_reports == ()
        assert result.max_positive_radial_deviation_mm == result.max_negative_radial_deviation_mm == 0.0
    elif radii[0] >= 0.0625:
        assert result.max_negative_radial_deviation_mm == 0.0
    else:
        assert result.max_positive_radial_deviation_mm == 0.0


@pytest.mark.parametrize("places", [True, 0, 7, "3"])
def test_empty_plan_still_rejects_invalid_precision(places: object) -> None:
    with pytest.raises(ValueError, match="decimal_places"):
        evaluate_plan_diameter_quantization(_numeric_plan(()), places)  # type: ignore[arg-type]


@pytest.mark.parametrize("update", [
    {"evaluated_moves_count": 0}, {"decimal_places": True}, {"decimal_places": 7},
    {"max_positive_radial_deviation_mm": 1.0}, {"max_negative_radial_deviation_mm": -1.0},
    {"is_boundary_safe": True}, {"boundary_status": "PASS"}, {"limitations": ()},
])
def test_aggregate_forgery_revalidation(update: dict[str, object]) -> None:
    result = evaluate_plan_diameter_quantization(_numeric_plan((0.0625, 0.061)), 2)
    with pytest.raises(ValidationError):
        TurningPlanQuantizationSummary.model_validate(result.model_copy(update=update))


def test_nested_forgery_and_plan_revalidation() -> None:
    plan = _numeric_plan((0.0625, 0.061))
    with pytest.raises(ValidationError):
        evaluate_plan_diameter_quantization(plan.model_copy(update={"physical_use_authorized": True}))
    bad_move = plan.operations[0].moves[0].model_copy(update={"start_point": (-1.0, 0.0)})
    bad_op = plan.operations[0].model_copy(update={"moves": (bad_move,)})
    with pytest.raises(ValidationError):
        evaluate_plan_diameter_quantization(plan.model_copy(update={"operations": (bad_op,)}))
    result = evaluate_plan_diameter_quantization(plan, 2)
    bad_report = result.move_reports[0].model_copy(update={"radial_deviation_mm": 1.0})
    with pytest.raises(ValidationError):
        TurningPlanQuantizationSummary.model_validate(result.model_copy(
            update={"move_reports": (bad_report, result.move_reports[1])}))
    with pytest.raises(ValidationError):
        result.decimal_places = 4


@pytest.mark.parametrize("radius", [1e-8, sys.float_info.max])
def test_bad_endpoint_aborts_aggregate(radius: float) -> None:
    with pytest.raises(ValueError):
        evaluate_plan_diameter_quantization(_numeric_plan((radius, radius)), 6)
