from pathlib import Path

import pytest

from app.modules.cad.features import FEATURE_RULE_VERSION, FeatureRecognizer
from app.modules.cad.kernel import OpenCascadeGeometryKernel


def _step_bytes(tmp_path: Path, shape: object, name: str) -> bytes:
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    target = tmp_path / f"{name}.step"
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    assert writer.Write(str(target)).name == "IFSelect_RetDone"
    return target.read_bytes()


def _analyze(tmp_path: Path, shape: object, name: str = "part"):
    return OpenCascadeGeometryKernel().analyze_step_with_features(
        _step_bytes(tmp_path, shape, name),
        recognizer=FeatureRecognizer(),
        unit="mm",
    )


def test_block_recognizes_planar_primitives_without_manufacturing_claim(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

    _geometry, result = _analyze(tmp_path, BRepPrimAPI_MakeBox(10, 20, 30).Shape())

    assert result is not None
    assert [feature.feature_type for feature in result.features] == ["PLANAR_FACE"] * 6
    assert all(feature.review_status.endswith("REQUIRES_HUMAN_REVIEW") for feature in result.features)
    assert not any("HOLE" in feature.feature_type for feature in result.features)


def test_external_cylinder_is_not_a_hole(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder

    _geometry, result = _analyze(tmp_path, BRepPrimAPI_MakeCylinder(4, 12).Shape())

    assert result is not None
    types = [feature.feature_type for feature in result.features]
    assert "CYLINDRICAL_FACE" in types
    assert "THROUGH_CYLINDRICAL_HOLE" not in types


def test_through_hole_has_traceable_dimensions_and_no_false_negative(tmp_path: Path) -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    block = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
    bore = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(5, 10, 0), gp_Dir(0, 0, 1)), 2, 30).Shape()
    _geometry, result = _analyze(tmp_path, BRepAlgoAPI_Cut(block, bore).Shape())

    assert result is not None
    holes = [
        feature for feature in result.features if feature.feature_type == "THROUGH_CYLINDRICAL_HOLE"
    ]
    assert len(holes) == 1
    dimensions = {dimension.name: dimension for dimension in holes[0].dimensions}
    assert dimensions["diameter"].value == pytest.approx(4.0, abs=result.tolerance)
    assert dimensions["depth"].value == pytest.approx(30.0, abs=result.tolerance)
    assert dimensions["diameter"].unit == "mm"
    assert holes[0].confidence_class == "HIGH_GEOMETRIC_EVIDENCE"
    assert holes[0].topology_refs[0].endswith("LOCAL_ANALYSIS_REFERENCE")
    assert result.rule_version == FEATURE_RULE_VERSION


def test_blind_hole_is_conservatively_deferred(tmp_path: Path) -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    block = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
    blind_bore = BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(5, 10, 20), gp_Dir(0, 0, 1)), 2, 10
    ).Shape()
    _geometry, result = _analyze(tmp_path, BRepAlgoAPI_Cut(block, blind_bore).Shape())

    assert result is not None
    assert "CYLINDRICAL_FACE" in [feature.feature_type for feature in result.features]
    assert "THROUGH_CYLINDRICAL_HOLE" not in [
        feature.feature_type for feature in result.features
    ]


def test_two_through_holes_are_independently_traceable(tmp_path: Path) -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    shape = BRepPrimAPI_MakeBox(20, 20, 10).Shape()
    for x_position in (5, 15):
        bore = BRepPrimAPI_MakeCylinder(
            gp_Ax2(gp_Pnt(x_position, 10, 0), gp_Dir(0, 0, 1)), 1.5, 10
        ).Shape()
        shape = BRepAlgoAPI_Cut(shape, bore).Shape()

    _geometry, result = _analyze(tmp_path, shape, "two-holes")

    assert result is not None
    holes = [
        feature for feature in result.features if feature.feature_type == "THROUGH_CYLINDRICAL_HOLE"
    ]
    assert len(holes) == 2
    assert holes[0].topology_refs != holes[1].topology_refs


def test_recognition_is_deterministic_for_same_step_and_rule(tmp_path: Path) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder

    content = _step_bytes(tmp_path, BRepPrimAPI_MakeCylinder(4, 12).Shape(), "repeat")
    kernel = OpenCascadeGeometryKernel()
    first_geometry, first = kernel.analyze_step_with_features(
        content, recognizer=FeatureRecognizer(), unit="mm"
    )
    second_geometry, second = kernel.analyze_step_with_features(
        content, recognizer=FeatureRecognizer(), unit="mm"
    )

    assert first_geometry == second_geometry
    assert first == second


def test_invalid_topology_never_produces_reliable_features() -> None:
    from app.modules.cad.kernel import KernelGeometry

    geometry = KernelGeometry(
        bounding_box=((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
        surface_area=0.0,
        volume=None,
        topology_valid=False,
        shape_type="SHAPE",
    )
    result = FeatureRecognizer().recognize(object(), geometry, "mm")

    assert result.status == "INVALID_TOPOLOGY"
    assert result.features == ()
