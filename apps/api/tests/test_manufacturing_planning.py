from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.parser import StepAnalysis
from app.modules.cad.service import CADDocumentAnalysis
from app.modules.engineering.manufacturing import ManufacturingPlanningService
from app.modules.engineering.manufacturing_schemas import ManufacturingPlanningRequest
from app.modules.engineering.schemas import AvailabilityValue
from app.modules.engineering.toolpath import ToolpathCandidateError, ToolpathCandidateService, ToolpathVerifier
from app.modules.engineering.toolpath_schemas import ToolpathCandidateRequest


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
    assert sum(region.volume or 0 for region in first.removal_regions) == pytest.approx(
        2448
    )
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
    assert "drilling_target_confirmation" in {
        item.field for item in result.missing_inputs
    }


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


def test_toolpath_verifier_rejects_protected_feed_and_generator_fails_closed(tmp_path: Path) -> None:
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
