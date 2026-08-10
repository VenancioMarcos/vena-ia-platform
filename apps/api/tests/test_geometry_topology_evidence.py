from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.evidence import GeometryEvidenceBuilder, GeometryEvidenceError
from app.modules.cad.kernel import GeometryKernelError, KernelGeometry, OpenCascadeGeometryKernel
from app.modules.cad.parser import StepAnalysis
from app.modules.cad.service import CADDocumentAnalysis


def _step_bytes(tmp_path: Path, shape: object, name: str) -> bytes:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path = tmp_path / f"{name}.step"
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    assert writer.Write(str(path)) == IFSelect_RetDone
    return path.read_bytes()


def test_box_evidence_is_replayable_and_connected(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeBox(10, 20, 30).Shape(), "box")
    kernel = OpenCascadeGeometryKernel()

    first_geometry, _features, first, _warning = kernel.analyze_step_with_evidence(
        content, unit="mm"
    )
    second_geometry, _features, second, _warning = kernel.analyze_step_with_evidence(
        content, unit="mm"
    )

    assert first_geometry == second_geometry
    assert first.status in {"AVAILABLE", "AVAILABLE_WITH_AMBIGUITY"}
    assert first.schema_version == "vena-ia.geometry-topology-evidence/v1"
    assert first.source_sha256 == hashlib.sha256(content).hexdigest()
    assert first.normalized_unit == "mm"
    assert first.normalization_scale == 1.0
    assert first.counts == {
        "EDGE": 12,
        "FACE": 6,
        "SHAPE": 1,
        "SHELL": 1,
        "SOLID": 1,
        "VERTEX": 8,
        "WIRE": 6,
    }
    assert [element.element_id for element in first.elements] == [
        element.element_id for element in second.elements
    ]
    assert [element.adjacent_to for element in first.elements] == [
        element.adjacent_to for element in second.elements
    ]
    assert {element.geometry_type for element in first.elements if element.kind == "FACE"} == {
        "PLANE"
    }
    assert {element.geometry_type for element in first.elements if element.kind == "EDGE"} == {
        "LINE"
    }
    assert all(element.contains for element in first.elements if element.kind == "FACE")
    assert all(element.connected_to for element in first.elements if element.kind == "EDGE")
    assert first.manufacturing_tolerance is None
    assert "MANUFACTURING_INTENT" in first.unsupported


@pytest.mark.parametrize(
    ("factory", "expected_surface"),
    [
        (
            lambda: (
                __import__("OCP.BRepPrimAPI", fromlist=["BRepPrimAPI_MakeCylinder"])
                .BRepPrimAPI_MakeCylinder(4, 12)
                .Shape()
            ),
            "CYLINDER",
        ),
        (
            lambda: (
                __import__("OCP.BRepPrimAPI", fromlist=["BRepPrimAPI_MakeCone"])
                .BRepPrimAPI_MakeCone(5, 2, 10)
                .Shape()
            ),
            "CONE",
        ),
        (
            lambda: (
                __import__("OCP.BRepPrimAPI", fromlist=["BRepPrimAPI_MakeSphere"])
                .BRepPrimAPI_MakeSphere(5)
                .Shape()
            ),
            "SPHERE",
        ),
        (
            lambda: (
                __import__("OCP.BRepPrimAPI", fromlist=["BRepPrimAPI_MakeTorus"])
                .BRepPrimAPI_MakeTorus(10, 2)
                .Shape()
            ),
            "TORUS",
        ),
    ],
)
def test_surface_classification_corpus(
    tmp_path: Path,
    factory,
    expected_surface: str,
) -> None:
    content = _step_bytes(tmp_path, factory(), expected_surface.lower())

    _geometry, _features, evidence, _warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(content, unit="mm")
    )

    assert expected_surface in {
        element.geometry_type for element in evidence.elements if element.kind == "FACE"
    }
    assert evidence.status in {"AVAILABLE", "AVAILABLE_WITH_AMBIGUITY"}


@pytest.mark.parametrize("curve_kind", ["ELLIPSE", "BSPLINE"])
def test_curve_classification_corpus(tmp_path: Path, curve_kind: str) -> None:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCP.Geom import Geom_Ellipse
    from OCP.GeomAPI import GeomAPI_PointsToBSpline
    from OCP.TColgp import TColgp_Array1OfPnt
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    if curve_kind == "ELLIPSE":
        curve = Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5, 2)
    else:
        points = TColgp_Array1OfPnt(1, 4)
        for index, point in enumerate(
            (gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(3, 2, 1), gp_Pnt(4, 0, 1)),
            start=1,
        ):
            points.SetValue(index, point)
        curve = GeomAPI_PointsToBSpline(points).Curve()
    content = _step_bytes(
        tmp_path,
        BRepBuilderAPI_MakeEdge(curve).Edge(),
        curve_kind.lower(),
    )

    _geometry, _features, evidence, _warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(content, unit="mm")
    )

    assert curve_kind in {
        element.geometry_type for element in evidence.elements if element.kind == "EDGE"
    }


def test_ambiguous_unit_fails_closed_without_topology_claim(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeBox(1, 2, 3).Shape(), "unit")

    geometry, _features, evidence, _warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(content, unit="UNKNOWN")
    )

    assert geometry.topology_valid is True
    assert evidence.status == "UNIT_AMBIGUOUS"
    assert evidence.elements == ()
    assert evidence.normalized_unit is None
    assert evidence.manufacturing_tolerance is None
    assert "AMBIGUOUS_SOURCE_UNIT" in evidence.unsupported


def test_feature_failure_does_not_suppress_general_evidence(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    class FailingRecognizer:
        def recognize(self, *_args, **_kwargs):
            raise GeometryKernelError("synthetic feature failure")

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeBox(1, 2, 3).Shape(), "feature-fail")

    geometry, features, evidence, warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(
            content,
            recognizer=FailingRecognizer(),  # type: ignore[arg-type]
            unit="mm",
        )
    )

    assert geometry.topology_valid is True
    assert features is None
    assert warning == "synthetic feature failure"
    assert evidence.status in {"AVAILABLE", "AVAILABLE_WITH_AMBIGUITY"}
    assert evidence.elements


def test_invalid_topology_is_explicit_and_withheld() -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    shape = BRepPrimAPI_MakeBox(1, 2, 3).Shape()
    invalid = KernelGeometry(
        bounding_box=((0, 0, 0), (1, 2, 3)),
        surface_area=22,
        volume=None,
        topology_valid=False,
        shape_type="SOLID",
    )

    evidence = GeometryEvidenceBuilder().build(
        shape,
        invalid,
        b"synthetic-invalid-topology",
        "mm",
        kernel="OpenCascade Technology",
        kernel_version="7.9.3",
        kernel_binding="cadquery-ocp==7.9.3.1.1",
    )

    assert evidence.status == "INVALID_TOPOLOGY"
    assert evidence.elements == ()
    assert evidence.topology_valid is False


def test_traversal_limit_fails_safely(monkeypatch: pytest.MonkeyPatch) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    import app.modules.cad.evidence as evidence_module

    monkeypatch.setattr(evidence_module, "MAX_TOPOLOGY_ELEMENTS", 1)
    shape = BRepPrimAPI_MakeBox(1, 2, 3).Shape()
    geometry = KernelGeometry(
        bounding_box=((0, 0, 0), (1, 2, 3)),
        surface_area=22,
        volume=6,
        topology_valid=True,
        shape_type="SOLID",
    )

    with pytest.raises(GeometryEvidenceError, match="resource limit"):
        GeometryEvidenceBuilder().build(
            shape,
            geometry,
            b"synthetic-limit",
            "mm",
            kernel="OpenCascade Technology",
            kernel_version="7.9.3",
            kernel_binding="cadquery-ocp==7.9.3.1.1",
        )


def test_openapi_exposes_additive_topology_evidence_contract() -> None:
    schema = app.openapi()["components"]["schemas"]["CADAnalysisResponse"]

    assert "topology_evidence" in schema["properties"]
    assert schema["properties"]["topology_evidence"]["$ref"].endswith(
        "/GeometryTopologyEvidenceContract"
    )


def test_cad_route_serializes_topology_evidence(client, tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeBox(2, 3, 4).Shape(), "route")
    geometry, _features, evidence, _warning = (
        OpenCascadeGeometryKernel().analyze_step_with_evidence(content, unit="mm")
    )
    service = MagicMock()
    service.analyze.return_value = CADDocumentAnalysis(
        document_id="document",
        source_filename="route.step",
        analysis=StepAnalysis(
            filename="route.step",
            schema="AP242",
            entity_count=1,
            entity_types={"MANIFOLD_SOLID_BREP": 1},
            cartesian_point_count=0,
            bounding_box=None,
            length_unit="mm",
            volume=None,
            volume_status="UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL",
        ),
        report="Synthetic topology evidence.",
        geometry=geometry,
        topology_evidence=evidence,
    )
    app.dependency_overrides[get_cad_analysis_service] = lambda: service
    try:
        response = client.post("/cad/documents/document/analysis")
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert response.status_code == 200
    payload = response.json()["topology_evidence"]
    assert payload["schema_version"] == "vena-ia.geometry-topology-evidence/v1"
    assert payload["counts"]["SHAPE"] == 1
    assert payload["source_sha256"] == hashlib.sha256(content).hexdigest()
    assert payload["manufacturing_tolerance"]["status"] == "NOT_PROVIDED"
    assert payload["human_review_required"] is True
    assert payload["executable_output"] is False
