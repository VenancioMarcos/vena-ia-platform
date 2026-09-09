"""Isolated, conservative external profile extraction for cylindrical steps."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.cad.axisymmetry import AnalyticFaceAxis, check_brep_axisymmetry, check_common_axis
from app.modules.engineering.turning_schemas import TurningProfile2D, TurningProfilePoint


Vector3 = tuple[float, float, float]
MAX_CYLINDRICAL_INTERVALS = 32


class TurningDatum(BaseModel):
    """Explicit finished-front origin and outward axial direction in world mm."""

    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False, frozen=True)
    origin_mm: Vector3
    axis_direction: Vector3

    @model_validator(mode="after")
    def validate_direction(self) -> TurningDatum:
        if not math.isclose(math.hypot(*self.axis_direction), 1.0, abs_tol=1e-9, rel_tol=0):
            raise ValueError("datum axis_direction must be a unit vector")
        return self


@dataclass(frozen=True)
class CylindricalInterval:
    radius_mm: float
    front_z_mm: float
    rear_z_mm: float


@dataclass(frozen=True)
class TurningProfileExtraction:
    status: Literal["PROFILE_AVAILABLE_REQUIRES_REVIEW", "AXISYMMETRY_FAILED"]
    profile: TurningProfile2D | None
    reasons: tuple[str, ...]
    limitations: tuple[str, ...] = (
        "CYLINDRICAL_EXTERNAL_STEPS_ONLY", "KERNEL_NUMERICAL_EQUIVALENCE_ONLY",
        "NO_CAM_POSTPROCESSOR_OR_PHYSICAL_AUTHORITY",
    )


def _reject(reason: str) -> TurningProfileExtraction:
    return TurningProfileExtraction("AXISYMMETRY_FAILED", None, (reason,))


def order_cylindrical_intervals(
    intervals: list[CylindricalInterval], *, linear_tolerance_mm: float,
) -> tuple[CylindricalInterval, ...]:
    """Order declared intervals and enforce a continuous, unambiguous Z domain."""
    if not math.isfinite(linear_tolerance_mm) or linear_tolerance_mm <= 0:
        raise ValueError("INVALID_TOLERANCE")
    if not intervals or len(intervals) > MAX_CYLINDRICAL_INTERVALS:
        raise ValueError("INTERVAL_LIMIT_OR_EMPTY")
    for interval in intervals:
        if (not all(math.isfinite(v) for v in (
                interval.radius_mm, interval.front_z_mm, interval.rear_z_mm))
                or interval.radius_mm <= linear_tolerance_mm
                or interval.front_z_mm - interval.rear_z_mm <= linear_tolerance_mm):
            raise ValueError("INVALID_CYLINDRICAL_INTERVAL")
    ordered = sorted(intervals, key=lambda item: (-item.front_z_mm, -item.rear_z_mm))
    for a, b in zip(ordered, ordered[1:]):
        if abs(a.rear_z_mm - b.front_z_mm) > linear_tolerance_mm:
            raise ValueError("DISCONTINUOUS_OR_OVERLAPPING_INTERVALS")
    return tuple(ordered)


def _world_point(datum: TurningDatum, z_mm: float, scale: float) -> Vector3:
    return tuple((origin + z_mm * direction) / scale
                 for origin, direction in zip(datum.origin_mm, datum.axis_direction))  # type: ignore[return-value]


def _no_residual_faces(first: Any, second: Any) -> bool:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut  # type: ignore[import-untyped]
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy  # type: ignore[import-untyped]
    from OCP.TopAbs import TopAbs_FACE  # type: ignore[import-untyped]
    from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]

    # Native boolean builders may adjust input tolerances: operate on copies.
    cut = BRepAlgoAPI_Cut(BRepBuilderAPI_Copy(first).Shape(), BRepBuilderAPI_Copy(second).Shape())
    return bool(cut.IsDone() and not TopExp_Explorer(cut.Shape(), TopAbs_FACE).More())


def extract_turning_profile(
    shape: Any, *, datum: TurningDatum, source_unit: str,
    linear_tolerance_mm: float, angular_tolerance_rad: float,
) -> TurningProfileExtraction:
    """Return a radial/Z polyline only after reconstructing the entire solid.

    source_unit describes actual BRep coordinates, not unverified STEP metadata.
    No diameter conversion, guessed datum, tolerance-based volume shortcut or NC.
    """
    preliminary = check_brep_axisymmetry(
        shape, source_unit=source_unit, linear_tolerance_mm=linear_tolerance_mm,
        angular_tolerance_rad=angular_tolerance_rad,
    )
    if preliminary.status == "AXISYMMETRY_FAILED":
        return _reject(preliminary.reasons[0])
    try:
        from OCP.BRepAdaptor import BRepAdaptor_Surface  # type: ignore[import-untyped]
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse  # type: ignore[import-untyped]
        from OCP.BRepCheck import BRepCheck_Analyzer  # type: ignore[import-untyped]
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder  # type: ignore[import-untyped]
        from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt  # type: ignore[import-untyped]
        from OCP.TopAbs import TopAbs_FACE  # type: ignore[import-untyped]
        from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]
        from OCP.TopoDS import TopoDS  # type: ignore[import-untyped]

        datum = TurningDatum.model_validate(datum.model_dump())
        scale = {"mm": 1.0, "m": 1000.0, "in": 25.4}[source_unit]
        intervals: list[CylindricalInterval] = []
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        datum_axis = AnalyticFaceAxis("CYLINDER", datum.origin_mm, datum.axis_direction)
        while explorer.More():
            adapter = BRepAdaptor_Surface(TopoDS.Face_s(explorer.Current()))
            kind = adapter.GetType().name
            if kind == "GeomAbs_Cone":
                return _reject("CONICAL_PROFILE_NOT_IN_FIRST_INCREMENT")
            if kind == "GeomAbs_Cylinder":
                cylinder = adapter.Cylinder()
                position, direction = cylinder.Axis().Location(), cylinder.Axis().Direction()
                face_axis = AnalyticFaceAxis(
                    "CYLINDER", (position.X() * scale, position.Y() * scale, position.Z() * scale),
                    (direction.X(), direction.Y(), direction.Z()),
                )
                same = check_common_axis(
                    [datum_axis, face_axis], linear_tolerance_mm=linear_tolerance_mm,
                    angular_tolerance_rad=angular_tolerance_rad,
                )
                if same.status == "AXISYMMETRY_FAILED":
                    return _reject("DATUM_AXIS_MISMATCH")
                axial = []
                for v in (adapter.FirstVParameter(), adapter.LastVParameter()):
                    p = adapter.Value(adapter.FirstUParameter(), v)
                    axial.append(sum((coord * scale - origin) * direction
                                     for coord, origin, direction in zip(
                                         (p.X(), p.Y(), p.Z()), datum.origin_mm,
                                         datum.axis_direction)))
                intervals.append(CylindricalInterval(cylinder.Radius() * scale,
                                                     max(axial), min(axial)))
            explorer.Next()
        ordered = order_cylindrical_intervals(intervals, linear_tolerance_mm=linear_tolerance_mm)
        if abs(ordered[0].front_z_mm) > linear_tolerance_mm:
            return _reject("FINISHED_FRONT_DATUM_REQUIRED")
        rebuilt: Any = None
        # Include front/rear radial faces, leaving only the centerline unclosed.
        points = [TurningProfilePoint(radius_mm=0.0, z_mm=0.0)]
        front = 0.0
        for item in ordered:
            for radius, z in ((item.radius_mm, front), (item.radius_mm, item.rear_z_mm)):
                point = TurningProfilePoint(radius_mm=radius, z_mm=z)
                if not points or points[-1] != point:
                    points.append(point)
            axis = gp_Ax2(gp_Pnt(*_world_point(datum, item.rear_z_mm, scale)),
                          gp_Dir(*datum.axis_direction))
            cylinder_shape = BRepPrimAPI_MakeCylinder(
                axis, item.radius_mm / scale, (front - item.rear_z_mm) / scale,
            ).Shape()
            if rebuilt is None:
                rebuilt = cylinder_shape
            else:
                fuse = BRepAlgoAPI_Fuse(rebuilt, cylinder_shape)
                if not fuse.IsDone():
                    return _reject("RECONSTRUCTION_FAILED")
                rebuilt = fuse.Shape()
            front = item.rear_z_mm
        if rebuilt is None or not BRepCheck_Analyzer(rebuilt).IsValid():
            return _reject("RECONSTRUCTION_FAILED")
        if not (_no_residual_faces(shape, rebuilt) and _no_residual_faces(rebuilt, shape)):
            return _reject("GLOBAL_SOLID_RECONSTRUCTION_MISMATCH")
        points.append(TurningProfilePoint(radius_mm=0.0, z_mm=front))
        profile = TurningProfile2D(
            points=tuple(points), axis_origin=datum.origin_mm,
            axis_direction=datum.axis_direction, is_closed=False,
        )
        return TurningProfileExtraction("PROFILE_AVAILABLE_REQUIRES_REVIEW", profile, ())
    except ValueError as exc:
        known = {"INVALID_TOLERANCE", "INTERVAL_LIMIT_OR_EMPTY", "INVALID_CYLINDRICAL_INTERVAL",
                 "DISCONTINUOUS_OR_OVERLAPPING_INTERVALS"}
        return _reject(str(exc) if str(exc) in known else "INVALID_PROFILE_DATA")
    except Exception:
        return _reject("PROFILE_EXTRACTION_FAILED")
