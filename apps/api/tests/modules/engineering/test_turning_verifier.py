from __future__ import annotations

import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.profile_extractor import TurningDatum, extract_turning_profile
from app.modules.engineering.turning_planner import generate_turning_roughing_plan
from app.modules.engineering.turning_schemas import TurningStockCylinder
from app.modules.engineering.turning_toolpath_schemas import (
    SyntheticTurningParameters, TurningChuckFixture, TurningMotionType, TurningOperationPlan,
    TurningStaticExclusionZone, TurningToolEnvelope2D, TurningToolpathMove, TurningToolpathPlan,
    TurningVerificationReport,
)
from app.modules.engineering.turning_verifier import verify_toolpath_boundaries


def _fixture(z: float = -200.0) -> TurningChuckFixture:
    return TurningChuckFixture(z_chuck_plane_mm=z, jaw_clamping_diameter_mm=60.0,
                               safety_clearance_axial_mm=1.0)


def _tool(**updates: object) -> TurningToolEnvelope2D:
    return TurningToolEnvelope2D.model_validate({
        "tool_id": "synthetic-body", "shank_r_min_mm": 0.0, "shank_r_max_mm": 1.0,
        "shank_z_min_mm": 0.0, "shank_z_max_mm": 1.0, **updates,
    })


def _zone(**updates: object) -> TurningStaticExclusionZone:
    return TurningStaticExclusionZone.model_validate({
        "zone_id": "static-rectangle", "r_min_mm": 4.0, "r_max_mm": 6.0,
        "z_min_mm": -6.0, "z_max_mm": -4.0, **updates,
    })


def _plan(points: tuple[tuple[float, float], ...],
          kind: TurningMotionType = TurningMotionType.RAPID) -> TurningToolpathPlan:
    moves = tuple(TurningToolpathMove(start_point=a, end_point=b, motion_type=kind,
                                    feed_rate_type="MM_PER_REVOLUTION")
                  for a, b in zip(points, points[1:]))
    return TurningToolpathPlan(profile_id="synthetic-only", operations=(TurningOperationPlan(
        operation_id="test-operation", operation_type="ROUGH_TURNING",
        passes_count=len(moves) if kind == TurningMotionType.CUTTING else 0, moves=moves,
    ),), total_cutting_length_mm=sum(math.dist(a, b) for a, b in zip(points, points[1:]))
                              if kind == TurningMotionType.CUTTING else 0.0)


@pytest.mark.parametrize("name,diameter", [("cylinder_d50_l100", 60.0),
                                         ("stepped_d30_d60", 70.0)])
def test_generated_plan_has_only_declared_boundary_success(name: str, diameter: float) -> None:
    path = Path(__file__).parents[2] / "fixtures" / "cad" / "turning" / f"{name}.stp"
    shape, _ = OpenCascadeGeometryKernel()._load_step_shape(path.read_bytes())
    result = extract_turning_profile(shape, datum=TurningDatum(
        origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0)), source_unit="mm",
        linear_tolerance_mm=1e-6, angular_tolerance_rad=1e-7)
    assert result.profile is not None
    plan = generate_turning_roughing_plan(result.profile, TurningStockCylinder(
        diameter_mm=diameter, length_mm=110.0, face_allowance_mm=3.0),
        SyntheticTurningParameters(axial_depth_mm=1.0, radial_depth_mm=2.0,
            axial_allowance_mm=0.5, radial_allowance_mm=0.5, clearance_mm=1.0,
            feed_rate_type="MM_PER_REVOLUTION"))
    before = plan.model_dump_json()
    report = verify_toolpath_boundaries(plan, _fixture(), _tool(), ())
    assert report.boundary_status == "PASS" and report.declared_boundaries_passed
    assert not report.is_verified and not report.physical_use_authorized
    assert report.collision_status == "NOT_VALIDATED" and not report.executable_output
    assert len(report.limitations) == 2 and not report.violating_moves
    assert TurningVerificationReport.model_validate_json(report.model_dump_json()) == report
    assert report == verify_toolpath_boundaries(plan, _fixture(), _tool(), ())
    assert plan.model_dump_json() == before and not plan.is_collision_free


@pytest.mark.parametrize("kind", list(TurningMotionType))
def test_chuck_contact_all_motion_types_and_envelope(kind: TurningMotionType) -> None:
    plan = _plan(((10.0, 0.0), (10.0, -7.0)), kind)
    # Ideal point stops above -8, but local body reaches exactly that plane.
    report = verify_toolpath_boundaries(plan, _fixture(-9.0),
                                       _tool(shank_z_min_mm=-1.0), ())
    assert report.boundary_status == "CHUCK_COLLISION_DETECTED"
    assert report.violating_moves == (0,)
    assert not report.declared_boundaries_passed
    # Positive body offset cannot hide a point touching the chuck plane.
    assert verify_toolpath_boundaries(plan, _fixture(-8.0),
        _tool(shank_z_min_mm=1.0, shank_z_max_mm=2.0), ()).boundary_status == "CHUCK_COLLISION_DETECTED"


@pytest.mark.parametrize("kind", list(TurningMotionType))
def test_segment_crosses_zone_with_both_endpoints_outside(kind: TurningMotionType) -> None:
    report = verify_toolpath_boundaries(_plan(((1.0, -9.0), (9.0, -1.0)), kind),
                                       _fixture(), _tool(), (_zone(),))
    assert report.boundary_status == "DECLARED_ZONE_INTERFERENCE"
    assert report.violating_moves == (0,)


def test_swept_box_overlap_alone_does_not_imply_segment_intersection() -> None:
    # Swept broad-phase box overlaps, but diagonal R-Z=0 never reaches this rectangle.
    report = verify_toolpath_boundaries(_plan(((0.0, 0.0), (10.0, 10.0))), _fixture(),
        _tool(), (_zone(r_min_mm=0.0, r_max_mm=1.0, z_min_mm=8.0, z_max_mm=9.0),))
    assert report.boundary_status == "PASS"


def test_signed_offset_and_tangent_contact_not_just_ideal_point() -> None:
    plan = _plan(((10.0, -10.0), (10.0, 0.0)))
    tool = _tool(shank_r_min_mm=-6.0, shank_r_max_mm=-4.0)
    assert verify_toolpath_boundaries(plan, _fixture(), tool, (_zone(),)).violating_moves == (0,)
    tangent = _zone(r_min_mm=11.0, r_max_mm=12.0)
    assert verify_toolpath_boundaries(plan, _fixture(), _tool(), (tangent,)).violating_moves == (0,)
    just_clear = tangent.model_copy(update={"r_min_mm": math.nextafter(11.0, math.inf)})
    assert verify_toolpath_boundaries(plan, _fixture(), _tool(), (just_clear,)).boundary_status == "PASS"


def test_all_indices_across_operations_and_chuck_precedence() -> None:
    a = _plan(((10.0, 2.0), (10.0, -10.0))).operations[0]
    b = _plan(((10.0, -10.0), (10.0, 2.0))).operations[0]
    plan = TurningToolpathPlan(profile_id="two-operations", operations=(a, b), total_cutting_length_mm=0.0)
    report = verify_toolpath_boundaries(plan, _fixture(-10.0), _tool(),
        (_zone(r_min_mm=10.0, r_max_mm=11.0),))
    assert report.violating_moves == (0, 1)
    assert report.boundary_status == "CHUCK_COLLISION_DETECTED"


def test_empty_plan_not_evaluated_and_requires_valid_inputs() -> None:
    empty = TurningToolpathPlan(profile_id="empty", operations=(), total_cutting_length_mm=0.0)
    report = verify_toolpath_boundaries(empty, _fixture(), _tool(), ())
    assert report.boundary_status == "NOT_EVALUATED" and not report.declared_boundaries_passed
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(empty, _fixture().model_copy(update={"z_chuck_plane_mm": math.nan}), _tool(), ())


def test_negative_centerline_forgery_is_rejected_by_deep_revalidation() -> None:
    plan = _plan(((1.0, 0.0), (2.0, 0.0)))
    move = plan.operations[0].moves[0].model_copy(update={"end_point": (-1.0, 0.0)})
    operation = plan.operations[0].model_copy(update={"moves": (move,)})
    forged = plan.model_copy(update={"operations": (operation,)})
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(forged, _fixture(), _tool(), ())
    with pytest.raises(ValidationError):
        _plan(((1.0, 0.0), (-1.0, 0.0)))


@pytest.mark.parametrize("updates", [
    {"shank_z_min_mm": math.nan}, {"shank_r_max_mm": math.inf},
    {"shank_r_max_mm": 0.0}, {"shank_z_min_mm": 2.0},
    {"shank_r_min_mm": "0"}, {"orientation_quadrant": 3},
])
def test_invalid_tool_contracts(updates: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _tool(**updates)


def test_zone_fixture_and_collection_revalidation() -> None:
    plan = _plan(((1.0, 0.0), (2.0, 0.0)))
    with pytest.raises(ValidationError):
        _zone(r_min_mm=-1.0)
    with pytest.raises(ValidationError):
        _zone(z_min_mm=10.0)
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(plan, _fixture(), _tool(),
            (_zone().model_copy(update={"r_max_mm": math.inf}),))
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(plan, _fixture(), _tool().model_copy(update={"shank_z_max_mm": -1.0}), ())
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(plan, _fixture().model_copy(update={"safety_clearance_axial_mm": 0.0}), _tool(), ())
    with pytest.raises(ValueError, match="unique"):
        verify_toolpath_boundaries(plan, _fixture(), _tool(), (_zone(), _zone()))
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(plan, _fixture(), _tool(), [_zone()])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        verify_toolpath_boundaries(plan, _fixture(), _tool())  # type: ignore[call-arg]


def test_exact_arithmetic_extremes_and_degenerate_static_zone() -> None:
    # Finite inputs whose float subtraction would overflow are handled rationally.
    plan = _plan(((10.0, -1e308), (10.0, 1e308)))
    report = verify_toolpath_boundaries(plan, _fixture(-1.7e308), _tool(),
        (_zone(r_min_mm=10.0, r_max_mm=10.0, z_min_mm=0.0, z_max_mm=0.0),))
    assert report.boundary_status == "DECLARED_ZONE_INTERFERENCE"
    assert report.violating_moves == (0,)


def test_resource_limits_fail_closed() -> None:
    plan = _plan(tuple((1.0, float(i % 2)) for i in range(2002)))
    zones = tuple(_zone(zone_id=str(i)) for i in range(101))
    with pytest.raises(ValueError, match="budget"):
        verify_toolpath_boundaries(plan, _fixture(), _tool(), zones)
    with pytest.raises(ValidationError):
        verify_toolpath_boundaries(_plan(((1.0, 0.0), (2.0, 0.0))), _fixture(), _tool(),
                                  tuple(_zone(zone_id=str(i)) for i in range(129)))


@pytest.mark.parametrize("updates", [
    {"is_verified": True}, {"physical_use_authorized": True}, {"executable_output": True},
    {"collision_status": "VALIDATED"}, {"limitations": ()}, {"declared_boundaries_passed": False},
    {"violating_moves": (0,)},
])
def test_report_cannot_promote_authority_or_hide_limits(updates: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        TurningVerificationReport.model_validate({"boundary_status": "PASS",
            "declared_boundaries_passed": True, "violating_moves": (), **updates})
