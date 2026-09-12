"""Bounded preliminary analytic-axis checks, isolated from the CAD pipeline."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Literal, Sequence


Vector3 = tuple[float, float, float]
MAX_FACES = 512
LIMITATIONS = (
    "PRELIMINARY_ANALYTIC_AXES_ONLY",
    "NO_PROFILE_EXTRACTION_OR_GLOBAL_REVOLUTION_PROOF",
    "NO_MANUFACTURING_OR_PHYSICAL_AUTHORITY",
)


@dataclass(frozen=True)
class AnalyticFaceAxis:
    geometry_type: Literal["CYLINDER", "CONE"]
    origin_mm: Vector3
    direction: Vector3


@dataclass(frozen=True)
class AxisymmetryResult:
    status: Literal["AXISYMMETRY_PRELIMINARY_PASS", "AXISYMMETRY_FAILED"]
    reasons: tuple[str, ...]
    checked_faces: int
    limitations: tuple[str, ...] = LIMITATIONS


def _failed(reason: str, count: int = 0) -> AxisymmetryResult:
    return AxisymmetryResult("AXISYMMETRY_FAILED", (reason,), count)


def _vector_valid(vector: Vector3) -> bool:
    return len(vector) == 3 and all(
        type(value) in (int, float) and math.isfinite(value) for value in vector
    )


def _unit(vector: Vector3) -> Vector3 | None:
    if not _vector_valid(vector):
        return None
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or norm == 0:
        return None
    return (vector[0] / norm, vector[1] / norm, vector[2] / norm)


def _cross(a: Vector3, b: Vector3) -> Vector3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _parallel(a: Vector3, b: Vector3, angular_tolerance_rad: float) -> bool:
    return math.hypot(*_cross(a, b)) <= math.sin(angular_tolerance_rad)


def _tolerances_valid(linear: float, angular: float) -> bool:
    # Explicit numerical comparison budgets, not manufacturing tolerances.
    return (
        type(linear) in (int, float) and type(angular) in (int, float)
        and math.isfinite(linear) and math.isfinite(angular)
        and linear > 0 and 0 < angular < math.pi / 2
    )


def check_common_axis(
    faces: Sequence[AnalyticFaceAxis], *, linear_tolerance_mm: float,
    angular_tolerance_rad: float,
) -> AxisymmetryResult:
    """Compare every pair of analytic axis lines; not merely their directions."""
    if not _tolerances_valid(linear_tolerance_mm, angular_tolerance_rad):
        return _failed("INVALID_TOLERANCE")
    if not faces or len(faces) > MAX_FACES:
        return _failed("EMPTY_OR_EXCESSIVE_FACES")
    axes: list[tuple[Vector3, Vector3]] = []
    for face in faces:
        direction = _unit(face.direction)
        if (face.geometry_type not in {"CYLINDER", "CONE"}
                or not _vector_valid(face.origin_mm) or direction is None):
            return _failed("INVALID_ANALYTIC_AXIS", len(axes))
        axes.append((face.origin_mm, direction))
    for (origin_a, axis_a), (origin_b, axis_b) in combinations(axes, 2):
        if not _parallel(axis_a, axis_b, angular_tolerance_rad):
            return _failed("NON_PARALLEL_AXES", len(axes))
        delta = tuple(b - a for a, b in zip(origin_a, origin_b))
        displacement: Vector3 = (delta[0], delta[1], delta[2])
        if not _vector_valid(displacement):
            return _failed("NUMERIC_RANGE_EXCEEDED", len(axes))
        # Both directions, and every pair, avoid asymmetric tolerance decisions.
        distances = [math.hypot(*_cross(displacement, axis)) for axis in (axis_a, axis_b)]
        if any(not math.isfinite(d) or d > linear_tolerance_mm for d in distances):
            return _failed("NON_COLLINEAR_AXES", len(axes))
    return AxisymmetryResult("AXISYMMETRY_PRELIMINARY_PASS", (), len(axes))


def check_brep_axisymmetry(
    shape: Any, *, source_unit: str, linear_tolerance_mm: float,
    angular_tolerance_rad: float,
) -> AxisymmetryResult:
    """Inspect all faces of one solid in its actual BRep coordinate unit.

    Full analytic U spans are a conservative prerequisite, not a proof that
    trimmed faces form a globally axisymmetric or machinable external profile.
    Native kernel crashes/resource preemption remain outside this helper.
    """
    if not _tolerances_valid(linear_tolerance_mm, angular_tolerance_rad):
        return _failed("INVALID_TOLERANCE")
    scale = {"mm": 1.0, "m": 1000.0, "in": 25.4}.get(source_unit)
    if scale is None:
        return _failed("UNKNOWN_BREP_UNIT")
    try:
        from OCP.BRepAdaptor import BRepAdaptor_Surface  # type: ignore[import-untyped]
        from OCP.BRepCheck import BRepCheck_Analyzer  # type: ignore[import-untyped]
        from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID  # type: ignore[import-untyped]
        from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]
        from OCP.TopoDS import TopoDS  # type: ignore[import-untyped]

        if shape.IsNull() or shape.ShapeType() != TopAbs_SOLID:
            return _failed("SINGLE_SOLID_REQUIRED")
        if not BRepCheck_Analyzer(shape).IsValid():
            return _failed("INVALID_TOPOLOGY")
        axes: list[AnalyticFaceAxis] = []
        planes: list[Vector3] = []
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        count = 0
        while explorer.More():
            count += 1
            if count > MAX_FACES:
                return _failed("FACE_LIMIT_EXCEEDED", count)
            adapter = BRepAdaptor_Surface(TopoDS.Face_s(explorer.Current()))
            kind = adapter.GetType().name
            if kind in {"GeomAbs_Cylinder", "GeomAbs_Cone"}:
                span = adapter.LastUParameter() - adapter.FirstUParameter()
                if not math.isfinite(span) or not math.isclose(
                    span, math.tau, abs_tol=angular_tolerance_rad, rel_tol=0,
                ):
                    return _failed("PARTIAL_ANGULAR_FACE", count)
                primitive = adapter.Cylinder() if kind == "GeomAbs_Cylinder" else adapter.Cone()
                axis = primitive.Axis()
                point, direction = axis.Location(), axis.Direction()
                axes.append(AnalyticFaceAxis(
                    "CYLINDER" if kind == "GeomAbs_Cylinder" else "CONE",
                    (point.X() * scale, point.Y() * scale, point.Z() * scale),
                    (direction.X(), direction.Y(), direction.Z()),
                ))
            elif kind == "GeomAbs_Plane":
                normal = adapter.Plane().Axis().Direction()
                planes.append((normal.X(), normal.Y(), normal.Z()))
            else:
                return _failed("UNSUPPORTED_SURFACE", count)
            explorer.Next()
        result = check_common_axis(
            axes, linear_tolerance_mm=linear_tolerance_mm,
            angular_tolerance_rad=angular_tolerance_rad,
        )
        if result.status == "AXISYMMETRY_FAILED":
            return AxisymmetryResult(result.status, result.reasons, count)
        for plane in planes:
            normal_unit = _unit(plane)
            for face in axes:
                axis_unit = _unit(face.direction)
                if (normal_unit is None or axis_unit is None
                        or not _parallel(normal_unit, axis_unit, angular_tolerance_rad)):
                    return _failed("NON_AXIAL_PLANE", count)
        return AxisymmetryResult("AXISYMMETRY_PRELIMINARY_PASS", (), count)
    except Exception:
        # Do not expose native error text or turn failed extraction into a pass.
        return _failed("BREP_INSPECTION_FAILED")
