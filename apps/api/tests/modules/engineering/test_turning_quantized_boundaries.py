import math

import pytest
from pydantic import ValidationError

from app.modules.engineering.turning_quantization import (
    reconstruct_quantized_toolpath_plan, verify_quantized_plan_boundaries,
)
from app.modules.engineering.turning_toolpath_schemas import (
    TurningChuckFixture, TurningMotionType, TurningOperationPlan, TurningStaticExclusionZone,
    TurningToolEnvelope2D, TurningToolpathMove, TurningToolpathPlan,
)
from app.modules.engineering.turning_verifier import verify_toolpath_boundaries


def _plan(points: tuple[tuple[float, float], ...], kind: TurningMotionType) -> TurningToolpathPlan:
    moves = tuple(TurningToolpathMove(start_point=a, end_point=b, motion_type=kind,
                                    feed_rate_type="MM_PER_MINUTE")
                  for a, b in zip(points, points[1:]))
    return TurningToolpathPlan(profile_id="nominal-profile", operations=(TurningOperationPlan(
        operation_id="kept-id", operation_type="ROUGH_TURNING", moves=moves,
        passes_count=len(moves) if kind == TurningMotionType.CUTTING else 0,
    ),), total_cutting_length_mm=math.fsum(math.dist(m.start_point, m.end_point) for m in moves)
        if kind == TurningMotionType.CUTTING else 0.0)


def _bounds() -> tuple[TurningChuckFixture, TurningToolEnvelope2D]:
    return (TurningChuckFixture(z_chuck_plane_mm=-100.0, jaw_clamping_diameter_mm=2.0,
                               safety_clearance_axial_mm=1.0),
            TurningToolEnvelope2D(tool_id="synthetic", shank_r_min_mm=0.0, shank_r_max_mm=0.001,
                                 shank_z_min_mm=0.0, shank_z_max_mm=0.001))


@pytest.mark.parametrize("kind", list(TurningMotionType))
def test_quantization_can_introduce_continuous_zone_interference(kind: TurningMotionType) -> None:
    original = _plan(((0.0625, 0.0), (0.0625, -1.0)), kind)
    fixture, tool = _bounds()
    zone = TurningStaticExclusionZone(zone_id="mid-segment", r_min_mm=0.064,
                                     r_max_mm=0.08, z_min_mm=-0.6, z_max_mm=-0.4)
    assert verify_toolpath_boundaries(original, fixture, tool, (zone,)).declared_boundaries_passed
    rebuilt, report = verify_quantized_plan_boundaries(original, fixture, tool, (zone,), 2)
    assert rebuilt.operations[0].moves[0].start_point[0] == 0.065
    assert report.boundary_status == "DECLARED_ZONE_INTERFERENCE"
    assert report.violating_moves == (0,) and not report.declared_boundaries_passed
    assert not report.is_verified and not report.physical_use_authorized
    assert report.collision_status == "NOT_VALIDATED"


@pytest.mark.parametrize("kind", list(TurningMotionType))
def test_reconstruction_preserves_identity_z_and_recomputes_cut_length(kind: TurningMotionType) -> None:
    original = _plan(((0.0625, 0.0), (0.061, -1.0), (0.07, -2.0)), kind)
    snapshot = original.model_dump_json()
    fixture, tool = _bounds()
    assert verify_toolpath_boundaries(original, fixture, tool, ()).declared_boundaries_passed
    rebuilt, report = verify_quantized_plan_boundaries(original, fixture, tool, (), 2)
    assert report.declared_boundaries_passed and not report.executable_output
    assert original.model_dump_json() == snapshot
    assert rebuilt.profile_id == original.profile_id
    op = rebuilt.operations[0]
    assert op.operation_id == "kept-id" and op.operation_type == "ROUGH_TURNING"
    assert op.passes_count == original.operations[0].passes_count
    assert [(m.start_point, m.end_point) for m in op.moves] == [
        ((0.065, 0.0), (0.06, -1.0)), ((0.06, -1.0), (0.07, -2.0))]
    assert all(m.motion_type == kind and m.feed_rate_type == "MM_PER_MINUTE" for m in op.moves)
    expected = math.hypot(0.06-0.065, -1.0) + math.hypot(0.07-0.06, -1.0)
    assert rebuilt.total_cutting_length_mm == (expected if kind == TurningMotionType.CUTTING else 0.0)
    assert not rebuilt.is_collision_free and not rebuilt.executable_output
    assert not rebuilt.physical_use_authorized and rebuilt.collision_status == "NOT_VALIDATED"
    assert reconstruct_quantized_toolpath_plan(original, 2) == rebuilt


def test_empty_reconstruction_is_not_boundary_success() -> None:
    original = TurningToolpathPlan(profile_id="empty", operations=(), total_cutting_length_mm=0.0)
    rebuilt, report = verify_quantized_plan_boundaries(original, *_bounds(), (), 2)
    assert rebuilt == original
    assert report.boundary_status == "NOT_EVALUATED" and not report.declared_boundaries_passed


@pytest.mark.parametrize("kind", list(TurningMotionType))
def test_collapsed_moves_rejected_without_silent_deletion(kind: TurningMotionType) -> None:
    original = _plan(((0.0625, 0.0), (0.063, 0.0)), kind)
    with pytest.raises(ValidationError, match="zero-length"):
        reconstruct_quantized_toolpath_plan(original, 2)


@pytest.mark.parametrize("places", [0, 7, True, "3"])
def test_precision_rejected(places: object) -> None:
    with pytest.raises(ValueError):
        reconstruct_quantized_toolpath_plan(_plan((), TurningMotionType.RAPID), places)  # type: ignore[arg-type]


def test_forged_plan_and_fixture_rejected() -> None:
    original = _plan(((0.0625, 0.0), (0.0625, -1.0)), TurningMotionType.RAPID)
    with pytest.raises(ValidationError):
        reconstruct_quantized_toolpath_plan(original.model_copy(update={"is_collision_free": True}))
    fixture, tool = _bounds()
    with pytest.raises(ValidationError):
        verify_quantized_plan_boundaries(original, fixture.model_copy(
            update={"z_chuck_plane_mm": math.nan}), tool, ())


def test_unchanged_z_preserves_chuck_violation() -> None:
    original = _plan(((0.0625, -98.0), (0.0625, -99.0)), TurningMotionType.RETRACT)
    rebuilt, report = verify_quantized_plan_boundaries(original, *_bounds(), (), 2)
    assert rebuilt.operations[0].moves[0].end_point[1] == -99.0
    assert report.boundary_status == "CHUCK_COLLISION_DETECTED" and report.violating_moves == (0,)
