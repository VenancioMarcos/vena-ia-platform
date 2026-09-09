from __future__ import annotations

import math
from itertools import permutations

import pytest

from app.modules.cad.axisymmetry import (
    AnalyticFaceAxis,
    MAX_FACES,
    check_brep_axisymmetry,
    check_common_axis,
)


TOLERANCES = {"linear_tolerance_mm": 1e-6, "angular_tolerance_rad": 1e-7}
AXIS = AnalyticFaceAxis("CYLINDER", (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))


def test_collinear_axes_allow_translation_and_opposite_direction() -> None:
    axes = [AXIS, AnalyticFaceAxis("CONE", (0.0, 0.0, 20.0), (0.0, 0.0, -2.0))]
    for order in permutations(axes):
        result = check_common_axis(order, **TOLERANCES)
        assert result.status == "AXISYMMETRY_PRELIMINARY_PASS"
        assert "NO_PROFILE_EXTRACTION_OR_GLOBAL_REVOLUTION_PROOF" in result.limitations


@pytest.mark.parametrize("origin,direction,reason", [
    ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), "NON_COLLINEAR_AXES"),
    ((0.0, 0.0, 0.0), (0.0, 1.0, 1.0), "NON_PARALLEL_AXES"),
    ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), "INVALID_ANALYTIC_AXIS"),
    ((float("nan"), 0.0, 0.0), (0.0, 0.0, 1.0), "INVALID_ANALYTIC_AXIS"),
    ((0.0, 0.0, 0.0), (0.0, float("inf"), 1.0), "INVALID_ANALYTIC_AXIS"),
])
def test_bad_axes_fail_closed(origin: tuple, direction: tuple, reason: str) -> None:
    result = check_common_axis([AXIS, AnalyticFaceAxis("CYLINDER", origin, direction)],
                               **TOLERANCES)
    assert result.status == "AXISYMMETRY_FAILED"
    assert result.reasons == (reason,)


def test_pairwise_budget_is_independent_of_reference_axis() -> None:
    # Each outer axis is within tolerance of the middle, but not of each other.
    axes = [AnalyticFaceAxis("CYLINDER", (x, 0.0, 0.0), AXIS.direction)
            for x in (-0.75e-6, 0.0, 0.75e-6)]
    for order in permutations(axes):
        assert check_common_axis(order, **TOLERANCES).status == "AXISYMMETRY_FAILED"


@pytest.mark.parametrize("linear,angular", [
    (0.0, 1e-7), (-1.0, 1e-7), (float("nan"), 1e-7),
    (1e-6, 0.0), (1e-6, math.pi / 2), (1e-6, float("inf")), (True, 1e-7),
])
def test_bad_tolerances_cannot_approve_axes(linear: float, angular: float) -> None:
    result = check_common_axis([AXIS], linear_tolerance_mm=linear,
                               angular_tolerance_rad=angular)
    assert result.reasons == ("INVALID_TOLERANCE",)


def test_resource_limits_and_empty_inputs_fail_closed() -> None:
    for faces in ([], [AXIS] * (MAX_FACES + 1)):
        assert check_common_axis(faces, **TOLERANCES).status == "AXISYMMETRY_FAILED"


def test_tolerance_boundary_and_coordinate_overflow() -> None:
    near = AnalyticFaceAxis("CONE", (0.5e-6, 0.0, 1.0), AXIS.direction)
    assert check_common_axis([AXIS, near], **TOLERANCES).status == "AXISYMMETRY_PRELIMINARY_PASS"
    huge = [AnalyticFaceAxis("CYLINDER", (x, 0.0, 0.0), AXIS.direction)
            for x in (-1e308, 1e308)]
    assert check_common_axis(huge, **TOLERANCES).reasons == ("NUMERIC_RANGE_EXCEEDED",)


def test_brep_axis_distances_use_declared_coordinate_unit() -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    outer = BRepPrimAPI_MakeCylinder(10, 20).Shape()
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0.01, 0, -1), gp_Dir(0, 0, 1)), 2, 22)
    cut = BRepAlgoAPI_Cut(outer, hole.Shape())
    solid = TopExp_Explorer(cut.Shape(), TopAbs_SOLID).Current()
    tolerances = {"linear_tolerance_mm": 0.1, "angular_tolerance_rad": 1e-7}
    # Same raw coordinates: offset 0.01 mm versus 0.254 mm after inch conversion.
    assert check_brep_axisymmetry(solid, source_unit="mm",
                                 **tolerances).status == "AXISYMMETRY_PRELIMINARY_PASS"
    assert check_brep_axisymmetry(solid, source_unit="in",
                                 **tolerances).reasons == ("NON_COLLINEAR_AXES",)


@pytest.mark.parametrize("cone", [False, True])
def test_real_rotated_translated_brep(cone: bool) -> None:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    axis = gp_Ax2(gp_Pnt(12, -8, 30), gp_Dir(1, 1, -1))
    shape = (BRepPrimAPI_MakeCone(axis, 8, 4, 20).Shape() if cone
             else BRepPrimAPI_MakeCylinder(axis, 8, 20).Shape())
    result = check_brep_axisymmetry(shape, source_unit="mm", **TOLERANCES)
    assert result.status == "AXISYMMETRY_PRELIMINARY_PASS"
    assert result.checked_faces == 3


def test_real_brep_rejects_partial_cylinder_box_and_sphere() -> None:
    from OCP.BRepPrimAPI import (
        BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere,
    )

    for shape in [BRepPrimAPI_MakeCylinder(5, 10, math.pi).Shape(),
                  BRepPrimAPI_MakeBox(10, 20, 30).Shape(),
                  BRepPrimAPI_MakeSphere(5).Shape()]:
        assert check_brep_axisymmetry(shape, source_unit="mm",
                                     **TOLERANCES).status == "AXISYMMETRY_FAILED"


def test_real_brep_with_eccentric_hole_is_not_collinear() -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    outer = BRepPrimAPI_MakeCylinder(10, 20).Shape()
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(3, 0, -1), gp_Dir(0, 0, 1)), 2, 22)
    cut = BRepAlgoAPI_Cut(outer, hole.Shape())
    # Boolean result can wrap the one solid in a compound: select it explicitly.
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    solids = TopExp_Explorer(cut.Shape(), TopAbs_SOLID)
    solid = solids.Current()
    solids.Next()
    assert not solids.More()
    result = check_brep_axisymmetry(solid, source_unit="mm", **TOLERANCES)
    assert result.status == "AXISYMMETRY_FAILED"
    assert result.reasons == ("NON_COLLINEAR_AXES",)


def test_brep_missing_units_invalid_shape_and_compounds_fail_closed() -> None:
    from OCP.BRep import BRep_Builder
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape

    shape = BRepPrimAPI_MakeCylinder(5, 10).Shape()
    assert check_brep_axisymmetry(shape, source_unit="unknown",
                                 **TOLERANCES).reasons == ("UNKNOWN_BREP_UNIT",)
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    builder.Add(compound, shape)
    for unsupported in (TopoDS_Shape(), compound, object()):
        assert check_brep_axisymmetry(unsupported, source_unit="mm",
                                     **TOLERANCES).status == "AXISYMMETRY_FAILED"
