from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.profile_extractor import TurningDatum
from app.modules.engineering import turning_service as service
from app.modules.engineering.turning_schemas import TurningStockCylinder
from app.modules.engineering.turning_toolpath_schemas import (
    SyntheticTurningExecutionResult, SyntheticTurningMetadata, SyntheticTurningParameters,
    TurningChuckFixture, TurningToolEnvelope2D,
)


@lru_cache
def _shape(name: str = "cylinder_d50_l100") -> Any:
    path = Path(__file__).parents[2] / "fixtures" / "cad" / "turning" / f"{name}.stp"
    return OpenCascadeGeometryKernel()._load_step_shape(path.read_bytes())[0]


def _inputs(**updates: Any) -> dict[str, Any]:
    return {
        "step_brep_solid": _shape(), "brep_unit_scale": 1.0,
        "linear_tolerance_mm": 1e-6, "angular_tolerance_rad": 1e-7,
        "datum": TurningDatum(origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0)),
        "stock": TurningStockCylinder(diameter_mm=70.0, length_mm=110.0, face_allowance_mm=3.0),
        "params": SyntheticTurningParameters(axial_depth_mm=1.0, radial_depth_mm=2.0,
            axial_allowance_mm=0.5, radial_allowance_mm=0.5, clearance_mm=1.0,
            feed_rate_type="MM_PER_REVOLUTION"),
        "fixture": TurningChuckFixture(z_chuck_plane_mm=-200.0, jaw_clamping_diameter_mm=60.0,
                                       safety_clearance_axial_mm=2.0),
        "tool_envelope": TurningToolEnvelope2D(tool_id="synthetic-body", shank_r_min_mm=0.0,
            shank_r_max_mm=1.0, shank_z_min_mm=0.0, shank_z_max_mm=1.0),
        "exclusion_zones": (), "evaluated_at_utc": datetime(2026, 9, 9, tzinfo=UTC), **updates,
    }


def _run(**updates: Any) -> SyntheticTurningExecutionResult:
    result = service.orchestrate_synthetic_turning_pipeline(**_inputs(**updates))
    assert not result.is_physical_ready and not result.physical_use_authorized
    assert not result.executable_output and result.emission_status == "CONTROLLER_PROFILE_UNRESOLVED"
    return result


@pytest.mark.parametrize("name,minimum_radius", [("cylinder_d50_l100", 25.5),
                                               ("stepped_d30_d60", 15.5)])
def test_e2e_real_step_profile_plan_and_boundaries(name: str, minimum_radius: float) -> None:
    result = _run(step_brep_solid=_shape(name))
    assert result.pipeline_status == "SUCCESS_SYNTHETIC" and result.failure_reason is None
    assert result.profile is not None and result.plan is not None and result.verification is not None
    assert result.verification.declared_boundaries_passed and not result.verification.is_verified
    assert result.verification.collision_status == "NOT_VALIDATED" and not result.plan.is_collision_free
    assert result.plan.operations[-1].passes_count > 1
    assert min(m.end_point[0] for m in result.plan.operations[-1].moves) == minimum_radius
    assert result.metadata.brep_serialization_digest_sha256 is not None
    assert len(result.metadata.parameters_digest_sha256) == 64
    assert result.metadata.occt_binding_version is not None
    assert result.metadata.brep_serialization_format == "OCCT_BREP_ASCII_V3_NO_TRIANGLES_NO_NORMALS"
    assert SyntheticTurningExecutionResult.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("scale", [0.5, 0.0, -1.0, math.inf, -math.inf, math.nan])
def test_invalid_scale_aborts_before_geometry_and_cam(scale: float, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("invalid scale must not call a later stage")
    monkeypatch.setattr(service, "_copy_and_serialize", forbidden)
    monkeypatch.setattr(service, "extract_turning_profile", forbidden)
    monkeypatch.setattr(service, "generate_turning_roughing_plan", forbidden)
    result = _run(brep_unit_scale=scale)
    assert result.pipeline_status == "CAD_EXTRACTION_FAILED"
    assert result.failure_reason == "UNSUPPORTED_BREP_UNIT_SCALE"
    assert result.metadata.brep_serialization_digest_sha256 is None
    assert result.profile is result.plan is result.verification is None


@pytest.mark.parametrize("name", ["asymmetric_keyway", "pure_prism"])
def test_geometry_rejection_preserves_serialization_digest(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("CAD failure must not reach planning")
    monkeypatch.setattr(service, "generate_turning_roughing_plan", forbidden)
    result = _run(step_brep_solid=_shape(name))
    assert result.pipeline_status == "CAD_EXTRACTION_FAILED"
    assert result.metadata.brep_serialization_digest_sha256 is not None
    assert result.profile is result.plan is result.verification is None


def test_stock_failure_preserves_profile_and_aborts_verifier(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("planning failure must not reach verifier")
    monkeypatch.setattr(service, "verify_toolpath_boundaries", forbidden)
    result = _run(stock=TurningStockCylinder(diameter_mm=40.0, length_mm=110.0, face_allowance_mm=3.0))
    assert result.pipeline_status == "PLANNING_FAILED" and result.profile is not None
    assert result.failure_reason == "STOCK_DOES_NOT_CONTAIN_FINISHED_ENVELOPE"
    assert result.plan is result.verification is None


def test_chuck_failure_preserves_plan_and_report() -> None:
    result = _run(fixture=TurningChuckFixture(z_chuck_plane_mm=-50.0,
        jaw_clamping_diameter_mm=60.0, safety_clearance_axial_mm=2.0))
    assert result.pipeline_status == "BOUNDARY_VERIFICATION_FAILED"
    assert result.plan is not None and result.verification is not None
    assert result.verification.boundary_status == "CHUCK_COLLISION_DETECTED"
    assert result.verification.violating_moves and not result.verification.declared_boundaries_passed


def test_empty_plan_cannot_promote_to_success() -> None:
    values = _inputs()
    parameters = values["params"].model_copy(update={"axial_allowance_mm": 0.0, "radial_allowance_mm": 0.0})
    result = _run(stock=TurningStockCylinder(diameter_mm=50.0, length_mm=100.0, face_allowance_mm=0.0),
                  params=parameters)
    assert result.pipeline_status == "BOUNDARY_VERIFICATION_FAILED"
    assert result.verification is not None and result.verification.boundary_status == "NOT_EVALUATED"


def test_replay_and_input_changes_have_honest_hashes() -> None:
    before = service._copy_and_serialize(_shape())[1]
    first, replay = _run(), _run()
    assert first == replay and first.model_dump_json() == replay.model_dump_json()
    assert service._copy_and_serialize(_shape())[1] == before
    changed_time = _run(evaluated_at_utc=datetime(2026, 9, 10, tzinfo=UTC))
    assert changed_time.metadata.parameters_digest_sha256 != first.metadata.parameters_digest_sha256
    assert changed_time.metadata.brep_serialization_digest_sha256 == before
    changed_fixture = _run(fixture=_inputs()["fixture"].model_copy(update={"z_chuck_plane_mm": -300.0}))
    assert changed_fixture.metadata.parameters_digest_sha256 != first.metadata.parameters_digest_sha256
    changed_shape = _run(step_brep_solid=_shape("stepped_d30_d60"))
    assert changed_shape.metadata.parameters_digest_sha256 == first.metadata.parameters_digest_sha256
    assert changed_shape.metadata.brep_serialization_digest_sha256 != before
    with pytest.raises(ValidationError):
        first.metadata.parameters_digest_sha256 = "0" * 64


@pytest.mark.parametrize("stamp", [datetime(2026, 9, 9), datetime(2026, 9, 9,
                                      tzinfo=timezone(timedelta(hours=-3))), "2026-09-09T00:00:00Z"])
def test_timestamp_requires_explicit_aware_utc(stamp: Any) -> None:
    with pytest.raises(ValidationError):
        _run(evaluated_at_utc=stamp)


@pytest.mark.parametrize("scale", [1000.0, 25.4])
def test_actual_brep_units_are_explicit(scale: float) -> None:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Pnt, gp_Trsf
    transformation = gp_Trsf()
    transformation.SetScale(gp_Pnt(0.0, 0.0, 0.0), 1.0 / scale)
    shape = BRepBuilderAPI_Transform(_shape(), transformation, True).Shape()
    result = _run(step_brep_solid=shape, brep_unit_scale=scale)
    assert result.pipeline_status == "SUCCESS_SYNTHETIC"
    assert result.profile is not None
    assert result.profile.points[1].radius_mm == pytest.approx(25.0)


@pytest.mark.parametrize("stage,status", [
    ("_copy_and_serialize", "CAD_EXTRACTION_FAILED"),
    ("extract_turning_profile", "CAD_EXTRACTION_FAILED"),
    ("generate_turning_roughing_plan", "PLANNING_FAILED"),
    ("verify_toolpath_boundaries", "BOUNDARY_VERIFICATION_FAILED"),
])
def test_stage_exceptions_fail_closed_without_native_details(
    stage: str, status: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("untrusted diagnostic details")
    monkeypatch.setattr(service, stage, fail)
    result = _run()
    assert result.pipeline_status == status
    assert "untrusted" not in result.model_dump_json()
    assert (result.metadata.brep_serialization_digest_sha256 is None) == (stage == "_copy_and_serialize")


def test_input_revalidation_no_implicit_defaults_or_coercions() -> None:
    values = _inputs()
    for bad in ("1", True):
        with pytest.raises(ValidationError):
            _run(brep_unit_scale=bad)
    with pytest.raises(ValidationError):
        _run(datum=values["datum"].model_copy(update={"axis_direction": (0.0, 0.0, 2.0)}))
    with pytest.raises(ValidationError):
        _run(tool_envelope=values["tool_envelope"].model_copy(update={"shank_r_max_mm": math.nan}))
    with pytest.raises(ValidationError):
        _run(linear_tolerance_mm=math.inf)
    values.pop("exclusion_zones")
    with pytest.raises(TypeError):
        service.orchestrate_synthetic_turning_pipeline(**values)
    assert _run(step_brep_solid=object()).pipeline_status == "CAD_EXTRACTION_FAILED"


@pytest.mark.parametrize("updates", [
    {"is_physical_ready": True}, {"physical_use_authorized": True}, {"executable_output": True},
    {"emission_status": "READY"}, {"plan": None}, {"profile": None}, {"verification": None},
    {"failure_reason": "unexpected"}, {"pipeline_status": "CAD_EXTRACTION_FAILED", "failure_reason": "failure"},
])
def test_result_status_artifacts_and_authority_are_consistent(updates: dict[str, Any]) -> None:
    result = _run()
    with pytest.raises(ValidationError):
        SyntheticTurningExecutionResult.model_validate({**result.model_dump(), **updates})


def test_metadata_and_cross_artifact_forgery_rejected() -> None:
    result = _run()
    assert result.plan is not None
    forged_plan = result.plan.model_copy(update={"profile_id": "different"})
    with pytest.raises(ValidationError):
        SyntheticTurningExecutionResult.model_validate({**result.model_dump(), "plan": forged_plan})
    for changes in ({"limitations": ()}, {"parameters_digest_sha256": "not-a-digest"},
                    {"brep_serialization_format": None}):
        with pytest.raises(ValidationError):
            SyntheticTurningMetadata.model_validate({**result.metadata.model_dump(), **changes})
