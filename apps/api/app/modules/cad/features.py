from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.modules.cad.kernel import GeometryKernelError, KernelGeometry


FEATURE_RULE_VERSION = "1.0.0"
REVIEW_STATUS = "PRELIMINARY_GEOMETRIC_FEATURE_REQUIRES_HUMAN_REVIEW"
LOCAL_REFERENCE = "LOCAL_ANALYSIS_REFERENCE"
LINEAR_TOLERANCE = 1e-6
MAX_FACE_TRAVERSAL = 10_000


class FeatureRecognitionError(GeometryKernelError):
    pass


@dataclass(frozen=True)
class FeatureDimension:
    name: str
    value: float | None
    unit: str
    source: str
    status: str = "AVAILABLE"


@dataclass(frozen=True)
class GeometryFeature:
    feature_type: str
    confidence_class: str
    geometry_evidence: tuple[str, ...]
    dimensions: tuple[FeatureDimension, ...]
    topology_refs: tuple[str, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    sort_key: tuple[object, ...]
    review_status: str = REVIEW_STATUS


@dataclass(frozen=True)
class FeatureRecognitionResult:
    status: str
    features: tuple[GeometryFeature, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    uncertainty: str
    tolerance: float
    rule_version: str = FEATURE_RULE_VERSION


def _vector(direction: Any) -> tuple[float, float, float]:
    return (float(direction.X()), float(direction.Y()), float(direction.Z()))


def _point(point: Any) -> tuple[float, float, float]:
    return (float(point.X()), float(point.Y()), float(point.Z()))


def _rounded(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(round(value, 9) for value in values)


class FeatureRecognizer:
    """Conservative OCCT recognizer for traceable geometric evidence only."""

    def recognize(
        self,
        shape: object,
        geometry: KernelGeometry,
        unit: str,
    ) -> FeatureRecognitionResult:
        if not geometry.topology_valid:
            return FeatureRecognitionResult(
                status="INVALID_TOPOLOGY",
                features=(),
                warnings=("Invalid topology cannot produce reliable features.",),
                limitations=self._limitations(),
                uncertainty="NOT_RECOGNIZED",
                tolerance=LINEAR_TOLERANCE,
            )
        try:
            from OCP.BRepAdaptor import BRepAdaptor_Surface  # type: ignore[import-untyped]
            from OCP.BRepGProp import BRepGProp  # type: ignore[import-untyped]
            from OCP.GProp import GProp_GProps  # type: ignore[import-untyped]
            from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane  # type: ignore[import-untyped]
            from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED  # type: ignore[import-untyped]
            from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]
            from OCP.TopoDS import TopoDS  # type: ignore[import-untyped]
        except ImportError as exc:
            raise FeatureRecognitionError("Geometry kernel unavailable") from exc

        features: list[GeometryFeature] = []
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        face_index = 0
        while explorer.More():
            face_index += 1
            if face_index > MAX_FACE_TRAVERSAL:
                raise FeatureRecognitionError("Feature traversal resource limit exceeded")
            face = TopoDS.Face_s(explorer.Current())
            adapter = BRepAdaptor_Surface(face)
            props = GProp_GProps()
            BRepGProp.SurfaceProperties_s(face, props)
            area = float(props.Mass())
            topology_ref = f"face:{face_index}:{LOCAL_REFERENCE}"
            if adapter.GetType() == GeomAbs_Plane:
                plane = adapter.Plane()
                normal = _vector(plane.Axis().Direction())
                if face.Orientation() == TopAbs_REVERSED:
                    normal = (-normal[0], -normal[1], -normal[2])
                location = _point(plane.Location())
                features.append(
                    GeometryFeature(
                        feature_type="PLANAR_FACE",
                        confidence_class="HIGH_GEOMETRIC_EVIDENCE",
                        geometry_evidence=(
                            "OCCT surface type is GeomAbs_Plane.",
                            f"oriented_normal={_rounded(normal)}",
                            f"plane_location={_rounded(location)}",
                        ),
                        dimensions=(
                            FeatureDimension("area", area, f"{unit}2", "OCCT surface properties"),
                        ),
                        topology_refs=(topology_ref,),
                        assumptions=("Surface classification is geometric, not manufacturing intent.",),
                        limitations=("Does not imply support, datum, pocket or machining face.",),
                        sort_key=("PLANAR_FACE", *_rounded(location), *_rounded(normal), round(area, 9)),
                    )
                )
            elif adapter.GetType() == GeomAbs_Cylinder:
                cylinder = adapter.Cylinder()
                axis = _vector(cylinder.Axis().Direction())
                location = _point(cylinder.Location())
                radius = float(cylinder.Radius())
                extent = abs(float(adapter.LastVParameter() - adapter.FirstVParameter()))
                evidence = (
                    "OCCT surface type is GeomAbs_Cylinder.",
                    f"axis={_rounded(axis)}",
                    f"axis_location={_rounded(location)}",
                    f"surface_orientation={face.Orientation().name}",
                )
                dimensions = (
                    FeatureDimension("radius", radius, unit, "OCCT cylindrical surface"),
                    FeatureDimension("diameter", radius * 2.0, unit, "2 × OCCT radius"),
                    FeatureDimension("axial_extent", extent, unit, "OCCT cylinder V bounds"),
                    FeatureDimension("area", area, f"{unit}2", "OCCT surface properties"),
                )
                features.append(
                    GeometryFeature(
                        feature_type="CYLINDRICAL_FACE",
                        confidence_class="HIGH_GEOMETRIC_EVIDENCE",
                        geometry_evidence=evidence,
                        dimensions=dimensions,
                        topology_refs=(topology_ref,),
                        assumptions=("Surface classification is geometric, not a hole claim.",),
                        limitations=("Does not imply a manufacturable cylindrical hole.",),
                        sort_key=(
                            "CYLINDRICAL_FACE",
                            *_rounded(location),
                            *_rounded(axis),
                            round(radius, 9),
                        ),
                    )
                )
                if self._is_strict_through_hole(adapter, face, geometry, axis):
                    features.append(
                        GeometryFeature(
                            feature_type="THROUGH_CYLINDRICAL_HOLE",
                            confidence_class="HIGH_GEOMETRIC_EVIDENCE",
                            geometry_evidence=evidence
                            + (
                                "Cylinder is an inward-oriented solid boundary.",
                                "Both axial endpoints coincide with opposite shape envelope limits.",
                            ),
                            dimensions=(
                                FeatureDimension(
                                    "diameter", radius * 2.0, unit, "2 × OCCT radius"
                                ),
                                FeatureDimension(
                                    "depth", extent, unit, "OCCT cylinder axial extent"
                                ),
                            ),
                            topology_refs=(topology_ref,),
                            assumptions=(
                                "Strict rule supports axis-aligned, constant-radius through bores only.",
                            ),
                            limitations=(
                                "Does not infer drill, tool, operation, tolerance or manufacturability.",
                            ),
                            sort_key=(
                                "THROUGH_CYLINDRICAL_HOLE",
                                *_rounded(location),
                                *_rounded(axis),
                                round(radius, 9),
                            ),
                        )
                    )
            explorer.Next()

        ordered = tuple(sorted(features, key=lambda item: item.sort_key))
        return FeatureRecognitionResult(
            status="AVAILABLE" if ordered else "NOT_RECOGNIZED",
            features=ordered,
            warnings=() if ordered else ("No supported geometric feature was recognized.",),
            limitations=self._limitations(),
            uncertainty="VALIDATED_SYNTHETIC_CORPUS_BOUNDARY",
            tolerance=LINEAR_TOLERANCE,
        )

    @staticmethod
    def _is_strict_through_hole(
        adapter: Any,
        face: Any,
        geometry: KernelGeometry,
        axis: tuple[float, float, float],
    ) -> bool:
        from OCP.TopAbs import TopAbs_REVERSED  # type: ignore[import-untyped]

        if face.Orientation() != TopAbs_REVERSED:
            return False
        dominant = max(range(3), key=lambda index: abs(axis[index]))
        if not math.isclose(abs(axis[dominant]), 1.0, abs_tol=LINEAR_TOLERANCE):
            return False
        if any(
            abs(axis[index]) > LINEAR_TOLERANCE for index in range(3) if index != dominant
        ):
            return False
        cylinder = adapter.Cylinder()
        location = _point(cylinder.Location())
        first = float(adapter.FirstVParameter())
        last = float(adapter.LastVParameter())
        endpoints = sorted((location[dominant] + axis[dominant] * first, location[dominant] + axis[dominant] * last))
        limits = sorted(
            (geometry.bounding_box[0][dominant], geometry.bounding_box[1][dominant])
        )
        return all(
            math.isclose(endpoint, limit, abs_tol=LINEAR_TOLERANCE)
            for endpoint, limit in zip(endpoints, limits, strict=True)
        )

    @staticmethod
    def _limitations() -> tuple[str, ...]:
        return (
            "Recognition is preliminary and requires human review.",
            "Closed holes and slots are intentionally not recognized by rule 1.0.0.",
            "No manufacturing intent, manufacturability, CAM, toolpath or G-code is inferred.",
            "Topology references are local to one analysis execution.",
        )
