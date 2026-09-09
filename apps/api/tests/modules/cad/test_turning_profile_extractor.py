from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.modules.cad.axisymmetry import check_brep_axisymmetry
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.parser import StepTextParser
from app.modules.cad.profile_extractor import (
    CylindricalInterval,
    TurningDatum,
    extract_turning_profile,
    order_cylindrical_intervals,
)


FIXTURES = Path(__file__).parents[2] / "fixtures" / "cad" / "turning"
TOLERANCES = {"linear_tolerance_mm": 1e-6, "angular_tolerance_rad": 1e-7}
DATUM = TurningDatum(origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0))


def _load(name: str) -> object:
    content = (FIXTURES / f"{name}.stp").read_bytes()
    assert StepTextParser().parse(content).length_unit == "mm"
    shape, geometry = OpenCascadeGeometryKernel()._load_step_shape(content)
    assert geometry.topology_valid
    return shape


@pytest.mark.parametrize("name,expected", [
    ("cylinder_d50_l100", [(0.0, 0.0), (25.0, 0.0), (25.0, -100.0), (0.0, -100.0)]),
    ("stepped_d30_d60", [(0.0, 0.0), (15.0, 0.0), (15.0, -40.0),
                         (30.0, -40.0), (30.0, -100.0), (0.0, -100.0)]),
])
def test_real_step_extracts_ordered_radial_profile(name: str, expected: list[tuple]) -> None:
    shape = _load(name)
    first = extract_turning_profile(shape, datum=DATUM, source_unit="mm", **TOLERANCES)
    second = extract_turning_profile(shape, datum=DATUM, source_unit="mm", **TOLERANCES)
    assert first == second
    assert first.status == "PROFILE_AVAILABLE_REQUIRES_REVIEW"
    assert first.profile is not None
    actual = [(p.radius_mm, p.z_mm) for p in first.profile.points]
    assert len(actual) == len(expected)
    for point, target in zip(actual, expected):
        assert point == pytest.approx(target, abs=1e-6)
    assert all(a.z_mm >= b.z_mm for a, b in zip(first.profile.points, first.profile.points[1:]))
    assert first.profile.axis_origin == DATUM.origin_mm
    assert first.profile.is_closed is False


@pytest.mark.parametrize("name", ["asymmetric_keyway", "pure_prism"])
def test_real_step_non_revolution_fails_without_profile(name: str) -> None:
    result = extract_turning_profile(_load(name), datum=DATUM, source_unit="mm", **TOLERANCES)
    assert result.status == "AXISYMMETRY_FAILED"
    assert result.profile is None


def test_hollow_coaxial_solid_cannot_promote_preliminary_axis_pass() -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -101), gp_Dir(0, 0, 1)), 5, 102)
    cut = BRepAlgoAPI_Cut(_load("cylinder_d50_l100"), hole.Shape())
    shape = TopExp_Explorer(cut.Shape(), TopAbs_SOLID).Current()
    assert check_brep_axisymmetry(shape, source_unit="mm",
                                 **TOLERANCES).status == "AXISYMMETRY_PRELIMINARY_PASS"
    result = extract_turning_profile(shape, datum=DATUM, source_unit="mm", **TOLERANCES)
    assert result.status == "AXISYMMETRY_FAILED"
    assert result.profile is None


@pytest.mark.parametrize("datum", [
    TurningDatum(origin_mm=(1.0, 0.0, 0.0), axis_direction=(0.0, 0.0, 1.0)),
    TurningDatum(origin_mm=(0.0, 0.0, 1.0), axis_direction=(0.0, 0.0, 1.0)),
    TurningDatum(origin_mm=(0.0, 0.0, 0.0), axis_direction=(0.0, 0.0, -1.0)),
])
def test_datum_is_required_on_finished_front_and_axis(datum: TurningDatum) -> None:
    result = extract_turning_profile(_load("cylinder_d50_l100"), datum=datum,
                                     source_unit="mm", **TOLERANCES)
    assert result.status == "AXISYMMETRY_FAILED"


def test_unit_and_datum_invalid_values_do_not_create_profile() -> None:
    result = extract_turning_profile(_load("cylinder_d50_l100"), datum=DATUM,
                                     source_unit="UNKNOWN", **TOLERANCES)
    assert result.profile is None
    for origin, axis in [((float("nan"), 0.0, 0.0), (0.0, 0.0, 1.0)),
                         ((0.0, 0.0, 0.0), (0.0, 0.0, 2.0))]:
        with pytest.raises(ValidationError):
            TurningDatum(origin_mm=origin, axis_direction=axis)


def test_continuity_c0_preserves_shoulder_and_rejects_gap_overlap() -> None:
    first = CylindricalInterval(15, 0, -40)
    second = CylindricalInterval(30, -40, -100)
    assert order_cylindrical_intervals([second, first], linear_tolerance_mm=1e-6) == (first, second)
    for front in (-39.9, -40.1):
        with pytest.raises(ValueError, match="DISCONTINUOUS_OR_OVERLAPPING_INTERVALS"):
            order_cylindrical_intervals([first, CylindricalInterval(30, front, -100)],
                                       linear_tolerance_mm=1e-6)
    near = CylindricalInterval(30, -40 + 0.5e-6, -100)
    assert len(order_cylindrical_intervals([first, near], linear_tolerance_mm=1e-6)) == 2


def test_cone_is_explicitly_outside_cylindrical_increment() -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    shape = BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(0, 0, -100), gp_Dir(0, 0, 1)), 25, 15, 100)
    result = extract_turning_profile(shape.Shape(), datum=DATUM, source_unit="mm", **TOLERANCES)
    assert result.reasons == ("CONICAL_PROFILE_NOT_IN_FIRST_INCREMENT",)
    assert result.profile is None


def test_profile_uses_explicit_world_datum_after_rotation_and_translation() -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    shape = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-90, 20, 30), gp_Dir(1, 0, 0)), 25, 100)
    datum = TurningDatum(origin_mm=(10.0, 20.0, 30.0), axis_direction=(1.0, 0.0, 0.0))
    result = extract_turning_profile(shape.Shape(), datum=datum, source_unit="mm", **TOLERANCES)
    assert result.profile is not None
    assert [(p.radius_mm, p.z_mm) for p in result.profile.points] == [
        (0.0, 0.0), (25.0, 0.0), (25.0, -100.0), (0.0, -100.0),
    ]


def test_global_reconstruction_rejects_void_even_if_preliminary_check_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeSphere
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from app.modules.cad.axisymmetry import AxisymmetryResult

    cut = BRepAlgoAPI_Cut(_load("cylinder_d50_l100"),
                         BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, -50), 5).Shape())
    shape = TopExp_Explorer(cut.Shape(), TopAbs_SOLID).Current()
    # A preliminary classifier cannot stand in for checking the whole solid.
    monkeypatch.setattr("app.modules.cad.profile_extractor.check_brep_axisymmetry",
                        lambda *args, **kwargs: AxisymmetryResult(
                            "AXISYMMETRY_PRELIMINARY_PASS", (), 4))
    result = extract_turning_profile(shape, datum=DATUM, source_unit="mm", **TOLERANCES)
    assert result.reasons == ("GLOBAL_SOLID_RECONSTRUCTION_MISMATCH",)
    assert result.profile is None


def test_fixture_generator_is_reproducible(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("turning_fixture_generator",
                                                 FIXTURES.parent / "generate_turning_step.py")
    assert spec is not None and spec.loader is not None
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    generator.generate(tmp_path)
    for fixture in FIXTURES.glob("*.stp"):
        regenerated = tmp_path / fixture.name
        assert regenerated.read_bytes() == fixture.read_bytes()
        content = regenerated.read_bytes()
        assert b"2026-09-09T00:00:00" in content
        assert StepTextParser().parse(content).length_unit == "mm"
