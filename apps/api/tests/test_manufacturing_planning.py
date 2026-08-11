from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from starlette.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.parser import StepAnalysis
from app.modules.cad.service import CADDocumentAnalysis
from app.modules.engineering.manufacturing import ManufacturingPlanningService
from app.modules.engineering.manufacturing_schemas import ManufacturingPlanningRequest
from app.modules.engineering.level2 import Level2Verifier
from app.modules.engineering.level2_schemas import KeepOutBounds, Level2VerificationRequest
from app.modules.engineering.blind_validation import ControlledBlindValidationService
from app.modules.engineering.blind_validation_schemas import ControlledBlindValidationRequest
from app.modules.engineering.schemas import AvailabilityValue
from app.modules.engineering.toolpath import (
    ToolpathCandidateError,
    ToolpathCandidateService,
    ToolpathVerifier,
)
from app.modules.engineering.toolpath_schemas import ToolpathCandidateRequest
from app.modules.engineering.postprocessor import RS274SafeSubsetVerifier, SyntheticPostprocessor
from app.modules.engineering.postprocessor_schemas import GCodeCandidateRequest


def _step_bytes(tmp_path: Path, shape: object, name: str = "manufacturing") -> bytes:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path = tmp_path / f"{name}.step"
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    assert writer.Write(str(path)) == IFSelect_RetDone
    return path.read_bytes()


def _analysis(tmp_path: Path) -> CADDocumentAnalysis:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeBox(10, 20, 30).Shape())
    geometry, _features, evidence, _warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(content, unit="mm")
    )
    return CADDocumentAnalysis(
        document_id="document",
        source_filename="part.step",
        analysis=StepAnalysis(
            filename="part.step",
            schema="AP242",
            entity_count=1,
            entity_types={"MANIFOLD_SOLID_BREP": 1},
            cartesian_point_count=0,
            bounding_box=None,
            length_unit="mm",
            volume=None,
            volume_status="UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL",
        ),
        report="Synthetic manufacturing corpus.",
        geometry=geometry,
        topology_evidence=evidence,
    )


def _recommendation(compatibility: str = "PRELIMINARY_COMPATIBILITY_CHECK:COMPATIBLE"):
    return SimpleNamespace(
        schema_version="vena-ia.engineering-recommendation/v1",
        status="PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW",
        compatibility=compatibility,
        operation="milling",
        preliminary_parameters={
            "spindle_speed": AvailabilityValue(status="AVAILABLE", value=4000, unit="rpm"),
            "feed_rate": AvailabilityValue(status="AVAILABLE", value=800, unit="mm/min"),
        },
        limitations=["Human validation required."],
        traceability=["authorized-catalogs"],
        data_versions={"material": "1", "machine": "1", "tool": "1"},
        rule_version="1.1.0",
    )


def _full_payload() -> dict[str, object]:
    return {
        "document_id": "document",
        "stock": {
            "status": "PROVIDED",
            "minimum": [-1, -1, -1],
            "maximum": [11, 21, 31],
            "unit": "mm",
            "source_ref": "user-input:synthetic-stock-v1",
        },
        "manufacturing_intent": "milling",
        "material_id": "material",
        "machine_id": "machine",
        "tool_id": "tool",
        "fixture": "Synthetic vise constraints reviewed by human",
        "datum_wcs_input": "Candidate Z+ datum/WCS requires human confirmation",
        "drawing_tolerance": "+/- 0.05 mm",
        "surface_finish": "Ra 3.2 um",
    }


def test_general_manufacturing_model_is_deterministic_and_non_executable(
    tmp_path: Path,
) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    service = ManufacturingPlanningService(cad, engineering)
    payload = ManufacturingPlanningRequest.model_validate(_full_payload())

    first = service.plan(payload)
    second = service.plan(payload)

    assert first.status == "READY_FOR_REVIEW"
    assert first.schema_version == "vena-ia.manufacturing-geometry-model/v1"
    assert first.planning_schema_version == "vena-ia.verified-process-plan/v1"
    assert first.stock.contains_final_geometry is True
    assert len(first.removal_regions) == 6
    assert sum(region.volume or 0 for region in first.removal_regions) == pytest.approx(2448)
    assert len(first.protected_regions) == 6
    assert first.accessibility_candidates
    assert first.datum_candidates
    assert first.wcs_candidates
    assert first.setup_candidates
    assert [item.operation_class for item in first.operation_candidates] == [
        "GEOMETRIC_ROUGHING_CANDIDATE",
        "FINISHING_REVIEW_CANDIDATE",
    ]
    assert first.operation_candidates[1].dependencies == [
        first.operation_candidates[0].candidate_id
    ]
    assert first.verification.deterministic_replay_hash == (
        second.verification.deterministic_replay_hash
    )
    assert first.verification.physical_validation is False
    assert first.executable_output is False
    assert all(not operation.executable_output for operation in first.operation_candidates)


def test_missing_inputs_are_requested_only_as_blocking_gates(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()

    result = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest(document_id="document")
    )

    assert result.status == "REQUIRES_INPUT"
    assert result.operation_candidates == []
    fields = {item.field for item in result.missing_inputs}
    assert {
        "stock",
        "manufacturing_intent",
        "material_id",
        "machine_id",
        "tool_id",
        "fixture",
        "datum_wcs_input",
    } <= fields
    engineering.recommend.assert_not_called()


def test_invalid_stock_fails_closed(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    payload = _full_payload()
    payload["stock"] = {
        "status": "PROVIDED",
        "minimum": [1, 1, 1],
        "maximum": [9, 19, 29],
        "unit": "mm",
        "source_ref": "user-input:undersized-stock",
    }

    result = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(payload)
    )

    assert result.status == "INVALID"
    assert result.stock.status == "INVALID"
    assert result.removal_regions == []
    assert result.operation_candidates == []


def test_no_false_drilling_claim_from_cylindrical_or_general_geometry(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    recommendation = _recommendation()
    recommendation.operation = "drilling"
    engineering.recommend.return_value = recommendation
    payload = _full_payload()
    payload["manufacturing_intent"] = "drilling"

    result = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(payload)
    )

    assert result.status == "REQUIRES_INPUT"
    assert result.operation_candidates == []
    assert "drilling_target_confirmation" in {item.field for item in result.missing_inputs}


def test_resource_mismatch_blocks_plan(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation(
        "PRELIMINARY_COMPATIBILITY_CHECK:INCOMPATIBLE"
    )

    result = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(_full_payload())
    )

    assert result.status == "BLOCKED_RESOURCE_MISMATCH"
    assert result.operation_candidates == []
    assert "INCOMPATIBLE" in result.verification.resource_compatibility


def _toolpath_request(model, operation_id: str) -> ToolpathCandidateRequest:
    return ToolpathCandidateRequest.model_validate(
        {
            "manufacturing_model": model,
            "operation_candidate_id": operation_id,
            "tool": {
                "tool_id": "synthetic-tool-0.5mm",
                "diameter_mm": 0.5,
                "flute_length_mm": 10,
            },
            "machine_minimum": [-10, -10, -10],
            "machine_maximum": [20, 30, 50],
            "clearance_z_mm": 40,
            "retract_z_mm": 35,
            "feed_mm_min": 800,
        }
    )


def test_toolpath_candidate_is_bounded_deterministic_and_non_executable(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    model = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(_full_payload())
    )
    operation_id = model.operation_candidates[0].candidate_id
    request = _toolpath_request(model, operation_id)

    first = ToolpathCandidateService().create(request)
    second = ToolpathCandidateService().create(request)

    assert first.status == "CANDIDATE_FOR_VALIDATION"
    assert first.schema_version == "vena-ia.toolpath-candidate/v1"
    assert first.executable_output is False
    assert first.production_authority is False
    assert all(segment.primitive == "LINEAR" for segment in first.segments)
    assert first.verification.status == "PASS_REQUIRES_HUMAN_REVIEW"
    assert first.verification.deterministic_replay_hash == (
        second.verification.deterministic_replay_hash
    )


def test_toolpath_verifier_rejects_protected_feed_and_generator_fails_closed(
    tmp_path: Path,
) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    model = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(_full_payload())
    )
    generated = ToolpathCandidateService().create(
        _toolpath_request(model, model.operation_candidates[0].candidate_id)
    )
    forged = generated.model_copy(
        update={
            "segments": [
                generated.segments[0].model_copy(
                    update={
                        "motion": "FEED_CANDIDATE",
                        "feed_mm_min": 800,
                        "start": (5.0, 10.0, 15.0),
                        "end": (5.0, 10.0, 15.0),
                    }
                )
            ]
        }
    )
    assert ToolpathVerifier().verify(forged, model).status == "REJECTED"

    invalid = _toolpath_request(model, model.operation_candidates[0].candidate_id)
    invalid = invalid.model_copy(update={"clearance_z_mm": 51})
    with pytest.raises(ToolpathCandidateError, match="Clearance"):
        ToolpathCandidateService().create(invalid)


def test_synthetic_postprocessor_and_independent_rs274_verifier(tmp_path: Path) -> None:
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    model = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(_full_payload())
    )
    path = ToolpathCandidateService().create(
        _toolpath_request(model, model.operation_candidates[0].candidate_id)
    )
    result = SyntheticPostprocessor().generate(GCodeCandidateRequest(toolpath=path))

    assert result.classification == "CANDIDATE_FOR_VALIDATION"
    assert result.production_authority is False
    assert result.executable_output is False
    assert result.program.startswith("G21\nG17\nG90\nG94\n")
    assert result.program.endswith("M30")
    assert result.verification.status == "PASS_REQUIRES_HUMAN_REVIEW"
    assert (
        RS274SafeSubsetVerifier().verify("G21\nG17\nG90\nG94\nG2 X1 Y1\nM30", "x").status
        == "REJECTED"
    )


def _controlled_validation_artifacts(tmp_path: Path):
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    engineering = MagicMock()
    engineering.recommend.return_value = _recommendation()
    model = ManufacturingPlanningService(cad, engineering).plan(
        ManufacturingPlanningRequest.model_validate(_full_payload())
    )
    path = ToolpathCandidateService().create(
        _toolpath_request(model, model.operation_candidates[0].candidate_id)
    )
    gcode = SyntheticPostprocessor().generate(GCodeCandidateRequest(toolpath=path))
    level2_request = Level2VerificationRequest(
        manufacturing_model=model,
        toolpath=path,
    )
    level2 = Level2Verifier().verify(level2_request)
    return model, path, gcode, level2


def test_level2_reconstructs_deterministically_without_reusing_generator(
    tmp_path: Path,
) -> None:
    model, path, _gcode, first = _controlled_validation_artifacts(tmp_path)
    second = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=model, toolpath=path)
    )

    assert first.status == "PASS_REQUIRES_HUMAN_REVIEW"
    assert first.target_coverage == "COMPLETE"
    assert first.simplified_sweep_volume_mm3 > 0
    assert first.replay_hash == second.replay_hash
    assert first.physical_validation is False


def test_level2_rejects_incomplete_and_inconsistent_trajectory(tmp_path: Path) -> None:
    model, path, _gcode, _level2 = _controlled_validation_artifacts(tmp_path)
    incomplete = path.model_copy(
        update={
            "segments": [
                segment.model_copy(update={"target_region_id": None})
                if segment.motion == "FEED_CANDIDATE"
                else segment
                for segment in path.segments
            ]
        }
    )
    inconsistent = path.model_copy(
        update={
            "segments": [
                path.segments[0],
                path.segments[1].model_copy(update={"start": (-9.0, -9.0, 39.0)}),
                *path.segments[2:],
            ]
        }
    )

    incomplete_result = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=model, toolpath=incomplete)
    )
    inconsistent_result = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=model, toolpath=inconsistent)
    )

    assert incomplete_result.status == "REJECTED"
    assert incomplete_result.target_coverage == "INCOMPLETE"
    assert inconsistent_result.status == "REJECTED"
    assert any("discontinuity" in reason for reason in inconsistent_result.rejected_reasons)


def test_level2_rejects_gouge_rapid_and_fixture_keepout(tmp_path: Path) -> None:
    model, path, _gcode, _level2 = _controlled_validation_artifacts(tmp_path)
    protected_point = (5.0, 10.0, 15.0)
    feed_index = next(
        index for index, segment in enumerate(path.segments) if segment.motion == "FEED_CANDIDATE"
    )
    forged_segments = list(path.segments)
    forged_segments[feed_index] = forged_segments[feed_index].model_copy(
        update={"start": protected_point, "end": protected_point}
    )
    forged_segments[0] = forged_segments[0].model_copy(update={"end": protected_point})
    forged = path.model_copy(update={"segments": forged_segments})
    keepout = KeepOutBounds(
        minimum=(-10.5, -10.5, 39.5),
        maximum=(-9.5, -9.5, 40.5),
        source_ref="synthetic-fixture-envelope",
    )

    result = Level2Verifier().verify(
        Level2VerificationRequest(
            manufacturing_model=model,
            toolpath=forged,
            fixture_keep_outs=[keepout],
        )
    )

    assert result.status == "REJECTED"
    assert result.gouge_detected is True
    assert result.protected_surface_violation is True
    assert result.rapid_collision_detected is True
    assert result.fixture_collision_detected is True


def test_level2_fails_closed_for_stock_and_nonfinite_evidence(tmp_path: Path) -> None:
    model, path, _gcode, _level2 = _controlled_validation_artifacts(tmp_path)
    missing_stock = model.model_copy(
        update={"stock": model.stock.model_copy(update={"minimum": None})}
    )
    insufficient_stock = model.model_copy(
        update={
            "stock": model.stock.model_copy(
                update={"status": "INVALID", "contains_final_geometry": False}
            )
        }
    )
    nonfinite = path.model_copy(
        update={
            "segments": [
                path.segments[0].model_copy(update={"end": (float("nan"), 0.0, 0.0)}),
                *path.segments[1:],
            ]
        }
    )

    missing_result = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=missing_stock, toolpath=path)
    )
    insufficient_result = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=insufficient_stock, toolpath=path)
    )
    nonfinite_result = Level2Verifier().verify(
        Level2VerificationRequest(manufacturing_model=model, toolpath=nonfinite)
    )

    assert missing_result.status == "REQUIRES_INPUT"
    assert insufficient_result.status == "REJECTED"
    assert nonfinite_result.status == "REJECTED"
    assert any("non-finite" in reason for reason in nonfinite_result.rejected_reasons)


def test_blind_harness_freezes_g0_g8_and_requires_real_g9_review(tmp_path: Path) -> None:
    model, path, gcode, level2 = _controlled_validation_artifacts(tmp_path)
    request = ControlledBlindValidationRequest(
        holdout_id="sealed-holdout-001",
        sealed_reference_hash="a" * 64,
        cad_hash="b" * 64,
        manufacturing_model=model,
        toolpath=path,
        gcode_candidate=gcode,
        level2_evidence=level2,
        questions_asked=["Are all safety gates supported by frozen evidence?"],
    )

    first = ControlledBlindValidationService().freeze(request)
    second = ControlledBlindValidationService().freeze(request)
    gates = {gate.gate: gate.status for gate in first.gates}

    assert all(gates[f"G{index}"] == "PASS" for index in range(9))
    assert gates["G9"] == "PENDING_REVIEW"
    assert first.cad_to_gcode_controlled_validation_ready is False
    assert first.physical_use_authorized is False
    assert first.replay_hash == second.replay_hash
    assert first.omissions == []
    assert first.false_positives == []


def test_level2_and_blind_routes_require_authenticated_identity(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    model, path, gcode, level2 = _controlled_validation_artifacts(tmp_path)
    level2_payload = Level2VerificationRequest(
        manufacturing_model=model,
        toolpath=path,
    ).model_dump(mode="json")
    blind_payload = ControlledBlindValidationRequest(
        holdout_id="sealed-holdout-route",
        sealed_reference_hash="c" * 64,
        cad_hash="d" * 64,
        manufacturing_model=model,
        toolpath=path,
        gcode_candidate=gcode,
        level2_evidence=level2,
    ).model_dump(mode="json")

    assert (
        client.post("/engineering/planning/level2-verification", json=level2_payload).status_code
        == 401
    )
    account = make_account("level2-route@vena-ia.dev")
    level2_response = client.post(
        "/engineering/planning/level2-verification",
        headers=account.headers,
        json=level2_payload,
    )
    blind_response = client.post(
        "/engineering/planning/controlled-blind-validation",
        headers=account.headers,
        json=blind_payload,
    )

    assert level2_response.status_code == 200, level2_response.text
    assert blind_response.status_code == 200, blind_response.text
    assert blind_response.json()["cad_to_gcode_controlled_validation_ready"] is False
    assert blind_response.json()["physical_use_authorized"] is False


def test_g9_authority_cannot_be_mass_assigned_or_forged(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    model, path, gcode, level2 = _controlled_validation_artifacts(tmp_path)
    legitimate = ControlledBlindValidationRequest(
        holdout_id="sealed-holdout-g9",
        sealed_reference_hash="e" * 64,
        cad_hash="f" * 64,
        manufacturing_model=model,
        toolpath=path,
        gcode_candidate=gcode,
        level2_evidence=level2,
    )
    baseline = ControlledBlindValidationService().freeze(legitimate)
    forged_payload = legitimate.model_dump(mode="json")
    forged_payload["human_review"] = {
        "reviewer_ref": "self-declared-reviewer",
        "decision": "APPROVED_FOR_CONTROLLED_VALIDATION",
        "evidence_ref": "self-declared-evidence",
    }

    with pytest.raises(ValidationError, match="human_review"):
        ControlledBlindValidationRequest.model_validate(forged_payload)

    account = make_account("forged-g9@vena-ia.dev")
    response = client.post(
        "/engineering/planning/controlled-blind-validation",
        headers=account.headers,
        json=forged_payload,
    )
    replay = ControlledBlindValidationService().freeze(legitimate)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "human_review"
    assert baseline.replay_hash == replay.replay_hash
    assert {gate.gate: gate.status for gate in replay.gates}["G9"] == "PENDING_REVIEW"
    assert replay.cad_to_gcode_controlled_validation_ready is False


def _catalog(
    client: TestClient,
    headers: dict[str, str],
    organization_id: str,
    kind: str,
    code: str,
    properties: dict[str, object],
) -> str:
    response = client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": code,
            "data_version": "2026.08",
            "source": "Synthetic organization-scoped planning corpus",
            "properties": properties,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_manufacturing_route_blocks_cross_organization_resources(
    client: TestClient,
    make_account,
    tmp_path: Path,
) -> None:
    owner = make_account("manufacturing-owner@vena-ia.dev")
    organization_id = client.post(
        "/organizations",
        headers=owner.headers,
        json={"name": "Manufacturing owner organization"},
    ).json()["id"]
    payload = _full_payload()
    payload["material_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "MATERIAL",
        "MAT-MFG",
        {"cutting_speed_m_min": 150, "feed_per_tooth_mm": 0.05},
    )
    payload["machine_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "MACHINE",
        "MACHINE-MFG",
        {"operations": ["milling"], "max_rpm": 10000, "max_feed_mm_min": 4000},
    )
    payload["tool_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "TOOL",
        "TOOL-MFG",
        {"operations": ["milling"], "diameter_mm": 10, "teeth": 2},
    )
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        outsider = make_account("manufacturing-outsider@vena-ia.dev")
        denied = client.post(
            "/engineering/planning/manufacturing-geometry",
            headers=outsider.headers,
            json=payload,
        )
        allowed = client.post(
            "/engineering/planning/manufacturing-geometry",
            headers=owner.headers,
            json=payload,
        )
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert denied.status_code == 404
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["status"] == "READY_FOR_REVIEW"
    assert allowed.json()["executable_output"] is False


def test_controlled_environment_runs_and_downloads_only_a_review_candidate(
    client: TestClient,
    make_account,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = make_account("controlled-environment-owner@vena-ia.dev")
    organization_id = client.post(
        "/organizations",
        headers=owner.headers,
        json={"name": "Controlled environment organization"},
    ).json()["id"]
    planning = _full_payload()
    planning["material_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "MATERIAL",
        "MAT-CONTROLLED",
        {"cutting_speed_m_min": 150, "feed_per_tooth_mm": 0.05},
    )
    planning["machine_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "MACHINE",
        "MACHINE-CONTROLLED",
        {"operations": ["milling"], "max_rpm": 10000, "max_feed_mm_min": 4000},
    )
    planning["tool_id"] = _catalog(
        client,
        owner.headers,
        organization_id,
        "TOOL",
        "TOOL-CONTROLLED",
        {"operations": ["milling"], "diameter_mm": 0.5, "teeth": 2},
    )
    payload = {
        "organization_id": organization_id,
        "planning": planning,
        "tool": {
            "tool_id": "synthetic-tool-0.5mm",
            "diameter_mm": 0.5,
            "flute_length_mm": 10,
        },
        "machine_minimum": [-10, -10, -10],
        "machine_maximum": [20, 30, 50],
        "clearance_z_mm": 40,
        "retract_z_mm": 35,
        "feed_mm_min": 800,
        "fixture_keep_outs": [],
        "holdout_id": "sealed-holdout-controlled-route",
        "sealed_reference_hash": "a" * 64,
        "questions_asked": ["Do G0-G8 have replayable evidence?"],
    }
    cad = MagicMock()
    cad.analyze.return_value = _analysis(tmp_path)
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        run = client.post(
            "/engineering/controlled-environment/runs",
            headers=owner.headers,
            json=payload,
        )
        assert run.status_code == 200, run.text
        result = run.json()
        download_payload = {
            "organization_id": organization_id,
            "gcode_candidate": result["gcode_candidate"],
            "blind_validation": result["blind_validation"],
            "digital_thread": result["digital_thread"],
            "download_token": result["download_token"],
        }
        download = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json=download_payload,
        )
        transport_forgery = client.post(
            "/engineering/controlled-environment/download"
            "?g9_state=APPROVED&physical_use_authorized=true",
            headers={
                **owner.headers,
                "X-Vena-IA-G9": "APPROVED",
                "X-Vena-IA-Physical-Use-Authorized": "true",
            },
            json=download_payload,
        )
        body_forgery = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json={**download_payload, "g9_state": "APPROVED"},
        )
        forged = dict(download_payload)
        forged["blind_validation"] = {
            **result["blind_validation"],
            "gates": [
                ({**gate, "status": "PASS"} if gate["gate"] == "G9" else gate)
                for gate in result["blind_validation"]["gates"]
            ],
        }
        rejected = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json=forged,
        )
        altered_candidate = {
            **download_payload,
            "gcode_candidate": {
                **result["gcode_candidate"],
                "program": result["gcode_candidate"]["program"] + "\nM30",
            },
        }
        altered_candidate_response = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json=altered_candidate,
        )
        altered_thread = {
            **download_payload,
            "digital_thread": {
                **result["digital_thread"],
                "physical_use_authorized": True,
            },
        }
        altered_thread_response = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json=altered_thread,
        )
        outsider = make_account("controlled-environment-outsider@vena-ia.dev")
        denied = client.post(
            "/engineering/controlled-environment/download?g9_state=APPROVED",
            headers={**outsider.headers, "X-Vena-IA-G9": "APPROVED"},
            json=download_payload,
        )

        member = make_account("controlled-environment-revoked@vena-ia.dev")
        team = client.post(
            f"/organizations/{organization_id}/teams",
            headers=owner.headers,
            json={"name": "Controlled environment team"},
        )
        assert team.status_code == 201, team.text
        membership = client.post(
            f"/organizations/{organization_id}/memberships",
            headers=owner.headers,
            json={
                "user_id": member.id,
                "role": "MEMBER",
                "team_id": team.json()["id"],
            },
        )
        assert membership.status_code == 201, membership.text
        member_run = client.post(
            "/engineering/controlled-environment/runs",
            headers=member.headers,
            json=payload,
        )
        assert member_run.status_code == 200, member_run.text
        member_result = member_run.json()
        member_download_payload = {
            "organization_id": organization_id,
            "gcode_candidate": member_result["gcode_candidate"],
            "blind_validation": member_result["blind_validation"],
            "digital_thread": member_result["digital_thread"],
            "download_token": member_result["download_token"],
        }
        revoked = client.delete(
            f"/organizations/{organization_id}/memberships/{membership.json()['id']}",
            headers=owner.headers,
        )
        assert revoked.status_code == 204
        revoked_download = client.post(
            "/engineering/controlled-environment/download",
            headers=member.headers,
            json=member_download_payload,
        )

        monkeypatch.setattr(
            "app.modules.engineering.controlled_environment.time.time",
            lambda: 4_000_000_000,
        )
        expired_download = client.post(
            "/engineering/controlled-environment/download",
            headers=owner.headers,
            json=download_payload,
        )
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert result["status"] == "READY_FOR_CONTROLLED_DOWNLOAD"
    assert result["non_production"] is True
    assert result["review_state"] == "REQUIRES_HUMAN_REVIEW"
    assert result["g9_state"] == "PENDING_AUTHORITATIVE_REVIEW"
    assert result["physical_use_authorized"] is False
    assert result["machine_send"] is False
    assert result["dnc"] is False
    assert result["nc_transfer"] is False
    assert result["cycle_start"] is False
    assert result["direct_machine_control"] is False
    assert result["digital_thread"]["status"] == "COMPLETE_NON_PRODUCTION"
    gates = {gate["gate"]: gate["status"] for gate in result["blind_validation"]["gates"]}
    assert all(gates[f"G{index}"] == "PASS" for index in range(9))
    assert gates["G9"] == "PENDING_REVIEW"
    assert download.status_code == 200, download.text
    assert download.headers["x-vena-ia-physical-use-authorized"] == "false"
    assert download.headers["x-vena-ia-review-state"] == "REQUIRES_HUMAN_REVIEW"
    assert download.text.endswith("M30")
    assert transport_forgery.status_code == 200
    assert transport_forgery.headers["x-vena-ia-physical-use-authorized"] == "false"
    assert transport_forgery.headers["x-vena-ia-review-state"] == "REQUIRES_HUMAN_REVIEW"
    assert body_forgery.status_code == 422
    assert rejected.status_code == 422
    assert altered_candidate_response.status_code == 422
    assert altered_thread_response.status_code == 422
    assert denied.status_code == 404
    assert revoked_download.status_code == 404
    assert expired_download.status_code == 422
