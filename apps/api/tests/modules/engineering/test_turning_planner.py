from __future__ import annotations

import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.profile_extractor import TurningDatum, extract_turning_profile
from app.modules.engineering.turning_planner import (
    SyntheticTurningPlanningError, generate_turning_roughing_plan,
)
from app.modules.engineering.turning_schemas import TurningProfile2D, TurningStockCylinder
from app.modules.engineering.turning_toolpath_schemas import (
    SyntheticTurningParameters, TurningMotionType, TurningToolpathMove, TurningToolpathPlan,
)


def _profile(name: str) -> TurningProfile2D:
    path = Path(__file__).parents[2] / "fixtures" / "cad" / "turning" / f"{name}.stp"
    shape, _ = OpenCascadeGeometryKernel()._load_step_shape(path.read_bytes())
    result = extract_turning_profile(
        shape, datum=TurningDatum(origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0)),
        source_unit="mm", linear_tolerance_mm=1e-6, angular_tolerance_rad=1e-7,
    )
    assert result.profile is not None
    return result.profile


def _parameters(**updates: object) -> SyntheticTurningParameters:
    return SyntheticTurningParameters.model_validate({
        "axial_depth_mm": 1.0, "radial_depth_mm": 2.0, "axial_allowance_mm": 0.5,
        "radial_allowance_mm": 0.5, "clearance_mm": 1.0,
        "feed_rate_type": "MM_PER_REVOLUTION", **updates,
    })


@pytest.mark.parametrize("name,diameter,target", [
    ("cylinder_d50_l100", 60.0, 25.5), ("stepped_d30_d60", 70.0, 15.5),
])
def test_real_profile_synthetic_passes_preserve_allowances(
    name: str, diameter: float, target: float,
) -> None:
    profile = _profile(name)
    stock = TurningStockCylinder(diameter_mm=diameter, length_mm=110.0, face_allowance_mm=3.0)
    parameters = _parameters()
    plan = generate_turning_roughing_plan(profile, stock, parameters)
    assert plan == generate_turning_roughing_plan(profile, stock, parameters)
    assert TurningToolpathPlan.model_validate_json(plan.model_dump_json()) == plan
    assert not plan.is_collision_free and plan.collision_status == "NOT_VALIDATED"
    assert not plan.executable_output and not plan.physical_use_authorized
    facing, roughing = plan.operations
    face_cuts = [m for m in facing.moves if m.motion_type == TurningMotionType.CUTTING]
    assert [m.end_point for m in face_cuts] == [(0.0, 2.0), (0.0, 1.0), (0.0, 0.5)]
    cuts = [m for m in roughing.moves if m.motion_type == TurningMotionType.CUTTING]
    radii = [diameter / 2, *(m.start_point[0] for m in cuts)]
    assert radii[-1] == target
    increments = [a - b for a, b in zip(radii, radii[1:])]
    targets = {target, 30.5} if name == "stepped_d30_d60" else {target}
    assert targets.issubset(set(radii))  # Each region reaches its exact allowance.
    for radius, step in zip(radii[1:], increments):
        assert 0 < step <= 2.0
        assert step == 2.0 or radius in targets
    for move in cuts:
        assert move.start_point[0] == move.end_point[0]
        if name == "stepped_d30_d60" and move.end_point[0] < 30.5:
            assert move.end_point[1] == -39.5  # Axial allowance at the shoulder.
        else:
            assert move.end_point[1] == -100.0
    all_moves = [move for operation in plan.operations for move in operation.moves]
    assert all(a.end_point == b.start_point for a, b in zip(all_moves, all_moves[1:]))
    assert all(min(m.start_point[0], m.end_point[0]) >= 0 for m in all_moves)
    assert plan.total_cutting_length_mm == pytest.approx(sum(
        math.dist(m.start_point, m.end_point) for m in all_moves
        if m.motion_type == TurningMotionType.CUTTING))


@pytest.mark.parametrize("diameter,length,face", [(49.0, 110.0, 3.0), (60.0, 100.0, 3.0),
                                               (60.0, 110.0, 0.0), (50.0, 110.0, 3.0)])
def test_stock_must_contain_profile_and_finish_allowances(
    diameter: float, length: float, face: float,
) -> None:
    stock = TurningStockCylinder(diameter_mm=diameter, length_mm=length, face_allowance_mm=face)
    with pytest.raises(SyntheticTurningPlanningError, match="STOCK_DOES_NOT_CONTAIN"):
        generate_turning_roughing_plan(_profile("cylinder_d50_l100"), stock, _parameters())


def test_undercut_and_taper_are_rejected() -> None:
    stock = TurningStockCylinder(diameter_mm=70.0, length_mm=110.0, face_allowance_mm=3.0)
    for points, reason in [
        ([(0, 0), (30, 0), (30, -40), (15, -40), (15, -100), (0, -100)], "UNDERCUT"),
        ([(0, 0), (15, 0), (30, -100), (0, -100)], "NON_CYLINDRICAL"),
    ]:
        data = _profile("stepped_d30_d60").model_dump()
        data["points"] = tuple({"radius_mm": float(r), "z_mm": float(z)} for r, z in points)
        with pytest.raises(SyntheticTurningPlanningError, match=reason):
            generate_turning_roughing_plan(TurningProfile2D.model_validate(data), stock, _parameters())


@pytest.mark.parametrize("field,value", [
    ("radial_depth_mm", 0.0), ("axial_depth_mm", -1.0),
    ("radial_allowance_mm", -1.0), ("clearance_mm", float("nan")),
    ("axial_allowance_mm", float("inf")), ("radial_depth_mm", "2.0"),
])
def test_invalid_or_coerced_synthetic_parameters(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        _parameters(**{field: value})


def test_negative_motion_radius_and_authority_overrides_rejected() -> None:
    with pytest.raises(ValidationError):
        TurningToolpathMove(start_point=(-1.0, 0.0), end_point=(0.0, 0.0),
                            motion_type=TurningMotionType.CUTTING,
                            feed_rate_type="MM_PER_MINUTE")
    baseline = {"profile_id": "synthetic", "operations": (), "total_cutting_length_mm": 0.0}
    for field in ("is_collision_free", "executable_output", "physical_use_authorized"):
        with pytest.raises(ValidationError):
            TurningToolpathPlan.model_validate({**baseline, field: True})
    with pytest.raises(ValidationError):
        TurningToolpathPlan.model_validate({**baseline, "collision_status": "VALIDATED"})


def test_no_stock_to_remove_and_resource_budget() -> None:
    profile = _profile("cylinder_d50_l100")
    stock = TurningStockCylinder(diameter_mm=50.0, length_mm=100.0, face_allowance_mm=0.0)
    parameters = _parameters(axial_allowance_mm=0.0, radial_allowance_mm=0.0)
    plan = generate_turning_roughing_plan(profile, stock, parameters)
    assert plan.total_cutting_length_mm == 0.0
    assert all(operation.passes_count == 0 and not operation.moves for operation in plan.operations)
    larger = TurningStockCylinder(diameter_mm=60.0, length_mm=110.0, face_allowance_mm=3.0)
    with pytest.raises(SyntheticTurningPlanningError, match="PASS_LIMIT_EXCEEDED"):
        generate_turning_roughing_plan(profile, larger, _parameters(radial_depth_mm=1e-300))


def test_fractional_depth_does_not_repeat_the_finish_boundary() -> None:
    stock = TurningStockCylinder(diameter_mm=51.0, length_mm=110.0, face_allowance_mm=3.0)
    plan = generate_turning_roughing_plan(_profile("cylinder_d50_l100"), stock,
                                         _parameters(radial_depth_mm=0.1, radial_allowance_mm=0.2))
    cuts = [m for m in plan.operations[1].moves if m.motion_type == TurningMotionType.CUTTING]
    assert len(cuts) == 3
    assert [m.start_point[0] for m in cuts] == pytest.approx([25.4, 25.3, 25.2])
