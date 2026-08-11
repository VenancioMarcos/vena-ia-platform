from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from itertools import combinations
from typing import Any, TypedDict

from app.modules.cad.kernel import GeometryKernelError, KernelGeometry


EVIDENCE_SCHEMA_VERSION = "vena-ia.geometry-topology-evidence/v1"
STABLE_ID_VERSION = "occt-canonical-geometry/v1"
MAX_TOPOLOGY_ELEMENTS = 50_000
MAX_RELATION_LINKS = 500_000
ROUND_DIGITS = 9
SUPPORTED_UNITS: dict[str, float] = {"mm": 1.0, "m": 1000.0, "in": 25.4}


class GeometryEvidenceError(GeometryKernelError):
    pass


class _CommonEvidence(TypedDict):
    source_sha256: str
    kernel: str
    kernel_version: str
    kernel_binding: str
    source_unit: str
    topology_valid: bool
    shape_type: str


@dataclass(frozen=True)
class TopologyElementEvidence:
    element_id: str
    kind: str
    geometry_type: str
    orientation: str
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] | None
    metrics: dict[str, float]
    contained_by: tuple[str, ...]
    contains: tuple[str, ...]
    adjacent_to: tuple[str, ...]
    connected_to: tuple[str, ...]
    ambiguity_group: str | None
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class GeometryTopologyEvidence:
    status: str
    source_sha256: str
    kernel: str
    kernel_version: str
    kernel_binding: str
    source_unit: str
    normalized_unit: str | None
    normalization_scale: float | None
    transform_representation: str
    topology_valid: bool
    shape_type: str
    counts: dict[str, int]
    elements: tuple[TopologyElementEvidence, ...]
    kernel_tolerance: float | None
    modeling_tolerance_max: float | None
    manufacturing_tolerance: float | None
    warnings: tuple[str, ...]
    unsupported: tuple[str, ...]
    limitations: tuple[str, ...]
    provenance: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    stable_id_version: str = STABLE_ID_VERSION
    schema_version: str = EVIDENCE_SCHEMA_VERSION


def unavailable_evidence(
    content: bytes,
    source_unit: str,
    *,
    kernel: str,
    kernel_version: str,
    kernel_binding: str,
    warning: str,
) -> GeometryTopologyEvidence:
    source_sha256 = hashlib.sha256(content).hexdigest()
    return GeometryTopologyEvidence(
        status="NOT_AVAILABLE",
        source_sha256=source_sha256,
        kernel=kernel,
        kernel_version=kernel_version,
        kernel_binding=kernel_binding,
        source_unit=source_unit,
        normalized_unit="mm" if source_unit in SUPPORTED_UNITS else None,
        normalization_scale=SUPPORTED_UNITS.get(source_unit),
        transform_representation="NOT_AVAILABLE",
        topology_valid=False,
        shape_type="UNKNOWN",
        counts={},
        elements=(),
        kernel_tolerance=None,
        modeling_tolerance_max=None,
        manufacturing_tolerance=None,
        warnings=(warning,),
        unsupported=("TOPOLOGY_EVIDENCE_EXTRACTION",),
        limitations=GeometryEvidenceBuilder._limitations(),
        provenance=(f"source:sha256:{source_sha256}",),
        evidence_refs=(),
    )


@dataclass(frozen=True)
class _Draft:
    shape: Any
    kind: str
    geometry_type: str
    orientation: str
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] | None
    metrics: dict[str, float]
    fingerprint: str
    element_id: str = ""
    ambiguity_group: str | None = None


def _rounded(value: float) -> float:
    if not math.isfinite(value):
        raise GeometryEvidenceError("Non-finite topology evidence")
    return round(float(value), ROUND_DIGITS)


def _point(value: Any) -> tuple[float, float, float]:
    return (_rounded(value.X()), _rounded(value.Y()), _rounded(value.Z()))


def _canonical_hash(payload: object, length: int = 20) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:length]


def _same(left: Any, right: Any) -> bool:
    return bool(left.IsSame(right))


class GeometryEvidenceBuilder:
    """Builds bounded, replayable geometric evidence without manufacturing inference."""

    def build(
        self,
        shape: Any,
        geometry: KernelGeometry,
        content: bytes,
        source_unit: str,
        *,
        kernel: str,
        kernel_version: str,
        kernel_binding: str,
    ) -> GeometryTopologyEvidence:
        source_sha256 = hashlib.sha256(content).hexdigest()
        common: _CommonEvidence = {
            "source_sha256": source_sha256,
            "kernel": kernel,
            "kernel_version": kernel_version,
            "kernel_binding": kernel_binding,
            "source_unit": source_unit,
            "topology_valid": geometry.topology_valid,
            "shape_type": geometry.shape_type,
        }
        if source_unit not in SUPPORTED_UNITS:
            return GeometryTopologyEvidence(
                **common,
                status="UNIT_AMBIGUOUS",
                normalized_unit=None,
                normalization_scale=None,
                transform_representation="NOT_AVAILABLE",
                counts={},
                elements=(),
                kernel_tolerance=None,
                modeling_tolerance_max=None,
                manufacturing_tolerance=None,
                warnings=("Source length unit is ambiguous; topology evidence withheld.",),
                unsupported=("AMBIGUOUS_SOURCE_UNIT",),
                limitations=self._limitations(),
                provenance=(f"source:sha256:{source_sha256}",),
                evidence_refs=(),
            )
        if not geometry.topology_valid:
            return GeometryTopologyEvidence(
                **common,
                status="INVALID_TOPOLOGY",
                normalized_unit="mm",
                normalization_scale=SUPPORTED_UNITS[source_unit],
                transform_representation="OCCT_TRANSFERRED_WORLD_COORDINATES",
                counts={},
                elements=(),
                kernel_tolerance=None,
                modeling_tolerance_max=None,
                manufacturing_tolerance=None,
                warnings=("Invalid topology cannot produce trusted element evidence.",),
                unsupported=("INVALID_TOPOLOGY",),
                limitations=self._limitations(),
                provenance=(f"source:sha256:{source_sha256}",),
                evidence_refs=(),
            )

        try:
            drafts = self._collect(shape)
            drafts = self._assign_ids(drafts, kernel_version)
            relations = self._relations(drafts)
            tolerances = [self._tolerance(item.shape, item.kind) for item in drafts]
        except GeometryEvidenceError:
            raise
        except Exception as exc:
            raise GeometryEvidenceError("Topology evidence extraction failed safely") from exc

        elements = tuple(
            TopologyElementEvidence(
                element_id=item.element_id,
                kind=item.kind,
                geometry_type=item.geometry_type,
                orientation=item.orientation,
                bounds=item.bounds,
                metrics=item.metrics,
                contained_by=relations[item.element_id]["contained_by"],
                contains=relations[item.element_id]["contains"],
                adjacent_to=relations[item.element_id]["adjacent_to"],
                connected_to=relations[item.element_id]["connected_to"],
                ambiguity_group=item.ambiguity_group,
                limitations=("Geometric classification does not imply manufacturing intent.",),
            )
            for item in sorted(drafts, key=lambda candidate: candidate.element_id)
        )
        counts = dict(sorted(Counter(item.kind for item in drafts).items()))
        ambiguous = sum(item.ambiguity_group is not None for item in drafts)
        return GeometryTopologyEvidence(
            **common,
            status="AVAILABLE_WITH_AMBIGUITY" if ambiguous else "AVAILABLE",
            normalized_unit="mm",
            normalization_scale=SUPPORTED_UNITS[source_unit],
            transform_representation="OCCT_TRANSFERRED_WORLD_COORDINATES",
            counts=counts,
            elements=elements,
            kernel_tolerance=1e-7,
            modeling_tolerance_max=max(tolerances, default=None),
            manufacturing_tolerance=None,
            warnings=(
                ()
                if not ambiguous
                else (f"{ambiguous} elements belong to canonical ambiguity groups.",)
            ),
            unsupported=("MANUFACTURING_INTENT", "PMI_MBD", "ASSEMBLY_SEMANTICS"),
            limitations=self._limitations(),
            provenance=(
                f"source:sha256:{source_sha256}",
                f"kernel:{kernel}:{kernel_version}",
                f"binding:{kernel_binding}",
                f"stable-id:{STABLE_ID_VERSION}",
            ),
            evidence_refs=tuple(item.element_id for item in elements),
        )

    def _collect(self, shape: Any) -> list[_Draft]:
        from OCP.BRep import BRep_Tool  # type: ignore[import-untyped]
        from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface  # type: ignore[import-untyped]
        from OCP.BRepBndLib import BRepBndLib  # type: ignore[import-untyped]
        from OCP.Bnd import Bnd_Box  # type: ignore[import-untyped]
        from OCP.BRepGProp import BRepGProp  # type: ignore[import-untyped]
        from OCP.GProp import GProp_GProps  # type: ignore[import-untyped]
        from OCP.TopAbs import (  # type: ignore[import-untyped]
            TopAbs_EDGE,
            TopAbs_FACE,
            TopAbs_REVERSED,
            TopAbs_SHELL,
            TopAbs_ShapeEnum,
            TopAbs_SOLID,
            TopAbs_VERTEX,
            TopAbs_WIRE,
        )
        from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]
        from OCP.TopoDS import TopoDS  # type: ignore[import-untyped]

        kinds = (
            ("SOLID", TopAbs_SOLID),
            ("SHELL", TopAbs_SHELL),
            ("FACE", TopAbs_FACE),
            ("WIRE", TopAbs_WIRE),
            ("EDGE", TopAbs_EDGE),
            ("VERTEX", TopAbs_VERTEX),
        )
        root_bounds = self._bounds(shape, Bnd_Box, BRepBndLib)
        root_type = TopAbs_ShapeEnum(shape.ShapeType()).name.removeprefix("TopAbs_")
        root_descriptor = {
            "kind": "SHAPE",
            "geometry_type": root_type,
            "orientation": shape.Orientation().name,
            "bounds": root_bounds,
            "metrics": {},
        }
        drafts: list[_Draft] = [
            _Draft(
                shape=shape,
                kind="SHAPE",
                geometry_type=root_type,
                orientation=shape.Orientation().name,
                bounds=root_bounds,
                metrics={},
                fingerprint=_canonical_hash(root_descriptor),
            )
        ]
        seen: list[Any] = []
        for kind, enum_value in kinds:
            explorer = TopExp_Explorer(shape, enum_value)
            while explorer.More():
                current = explorer.Current()
                if not any(_same(current, known) for known in seen):
                    seen.append(current)
                    typed = self._typed_shape(current, kind, TopoDS)
                    bounds = self._bounds(typed, Bnd_Box, BRepBndLib)
                    geometry_type = kind
                    metrics: dict[str, float] = {}
                    if kind == "FACE":
                        adapter = BRepAdaptor_Surface(typed)
                        geometry_type = self._surface_type(adapter.GetType().name)
                        props = GProp_GProps()
                        BRepGProp.SurfaceProperties_s(typed, props)
                        metrics = {"area": _rounded(props.Mass())}
                        if geometry_type == "PLANE":
                            plane = adapter.Plane()
                            direction = plane.Axis().Direction()
                            sign = -1.0 if typed.Orientation() == TopAbs_REVERSED else 1.0
                            metrics.update(
                                {
                                    "normal_x": _rounded(sign * direction.X()),
                                    "normal_y": _rounded(sign * direction.Y()),
                                    "normal_z": _rounded(sign * direction.Z()),
                                    "location_x": _rounded(plane.Location().X()),
                                    "location_y": _rounded(plane.Location().Y()),
                                    "location_z": _rounded(plane.Location().Z()),
                                }
                            )
                        elif geometry_type in {"CYLINDER", "CONE", "TORUS"}:
                            primitives = {
                                "CYLINDER": adapter.Cylinder,
                                "CONE": adapter.Cone,
                                "TORUS": adapter.Torus,
                            }
                            axis = primitives[geometry_type]().Axis().Direction()
                            metrics.update(
                                {
                                    "axis_x": _rounded(axis.X()),
                                    "axis_y": _rounded(axis.Y()),
                                    "axis_z": _rounded(axis.Z()),
                                }
                            )
                    elif kind == "EDGE":
                        adapter = BRepAdaptor_Curve(typed)
                        geometry_type = self._curve_type(adapter.GetType().name)
                        props = GProp_GProps()
                        BRepGProp.LinearProperties_s(typed, props)
                        metrics = {"length": _rounded(props.Mass())}
                    elif kind == "SOLID":
                        props = GProp_GProps()
                        BRepGProp.VolumeProperties_s(typed, props)
                        metrics = {"volume": _rounded(props.Mass())}
                    elif kind == "VERTEX":
                        metrics = dict(zip(("x", "y", "z"), _point(BRep_Tool.Pnt_s(typed))))
                    descriptor = {
                        "kind": kind,
                        "geometry_type": geometry_type,
                        "orientation": current.Orientation().name,
                        "bounds": bounds,
                        "metrics": metrics,
                    }
                    drafts.append(
                        _Draft(
                            shape=typed,
                            kind=kind,
                            geometry_type=geometry_type,
                            orientation=current.Orientation().name,
                            bounds=bounds,
                            metrics=metrics,
                            fingerprint=_canonical_hash(descriptor),
                        )
                    )
                    if len(drafts) > MAX_TOPOLOGY_ELEMENTS:
                        raise GeometryEvidenceError("Topology traversal resource limit exceeded")
                explorer.Next()
        return drafts

    @staticmethod
    def _typed_shape(current: Any, kind: str, topo_ds: Any) -> Any:
        converters = {
            "SOLID": topo_ds.Solid_s,
            "SHELL": topo_ds.Shell_s,
            "FACE": topo_ds.Face_s,
            "WIRE": topo_ds.Wire_s,
            "EDGE": topo_ds.Edge_s,
            "VERTEX": topo_ds.Vertex_s,
        }
        return converters[kind](current)

    @staticmethod
    def _bounds(
        shape: Any, box_class: Any, bound_library: Any
    ) -> tuple[tuple[float, float, float], tuple[float, float, float]] | None:
        box = box_class()
        bound_library.Add_s(shape, box)
        if box.IsVoid():
            return None
        xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
        return (
            (_rounded(xmin), _rounded(ymin), _rounded(zmin)),
            (_rounded(xmax), _rounded(ymax), _rounded(zmax)),
        )

    @staticmethod
    def _surface_type(name: str) -> str:
        mapping = {
            "GeomAbs_Plane": "PLANE",
            "GeomAbs_Cylinder": "CYLINDER",
            "GeomAbs_Cone": "CONE",
            "GeomAbs_Sphere": "SPHERE",
            "GeomAbs_Torus": "TORUS",
            "GeomAbs_BSplineSurface": "BSPLINE",
        }
        return mapping.get(name, "OTHER")

    @staticmethod
    def _curve_type(name: str) -> str:
        mapping = {
            "GeomAbs_Line": "LINE",
            "GeomAbs_Circle": "CIRCLE",
            "GeomAbs_Ellipse": "ELLIPSE",
            "GeomAbs_BSplineCurve": "BSPLINE",
        }
        return mapping.get(name, "OTHER")

    @staticmethod
    def _assign_ids(drafts: list[_Draft], kernel_version: str) -> list[_Draft]:
        groups: dict[tuple[str, str], list[_Draft]] = defaultdict(list)
        for item in drafts:
            groups[(item.kind, item.fingerprint)].append(item)
        result: list[_Draft] = []
        for (kind, fingerprint), group in sorted(groups.items()):
            ambiguity = (
                f"amb-{_canonical_hash([kernel_version, kind, fingerprint], 12)}"
                if len(group) > 1
                else None
            )
            for occurrence, item in enumerate(group, start=1):
                identity = [STABLE_ID_VERSION, kernel_version, kind, fingerprint, occurrence]
                result.append(
                    replace(
                        item,
                        element_id=f"{kind.lower()}-{_canonical_hash(identity)}",
                        ambiguity_group=ambiguity,
                    )
                )
        return result

    def _relations(self, drafts: list[_Draft]) -> dict[str, dict[str, tuple[str, ...]]]:
        from OCP.TopAbs import (  # type: ignore[import-untyped]
            TopAbs_EDGE,
            TopAbs_FACE,
            TopAbs_FORWARD,
            TopAbs_SHELL,
            TopAbs_SOLID,
            TopAbs_VERTEX,
            TopAbs_WIRE,
        )
        from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]

        child_types = {
            "SHAPE": (
                ("SOLID", TopAbs_SOLID),
                ("SHELL", TopAbs_SHELL),
                ("FACE", TopAbs_FACE),
                ("WIRE", TopAbs_WIRE),
                ("EDGE", TopAbs_EDGE),
                ("VERTEX", TopAbs_VERTEX),
            ),
            "SOLID": (("SHELL", TopAbs_SHELL),),
            "SHELL": (("FACE", TopAbs_FACE),),
            "FACE": (("WIRE", TopAbs_WIRE), ("EDGE", TopAbs_EDGE)),
            "WIRE": (("EDGE", TopAbs_EDGE),),
            "EDGE": (("VERTEX", TopAbs_VERTEX),),
        }
        contains: dict[str, set[str]] = defaultdict(set)
        contained_by: dict[str, set[str]] = defaultdict(set)
        transient_index: dict[tuple[str, int], list[_Draft]] = defaultdict(list)
        for item in drafts:
            transient_index[
                (item.kind, hash(item.shape.Oriented(TopAbs_FORWARD)))
            ].append(item)
        relation_links = 0
        for parent in drafts:
            for child_kind, enum_value in child_types.get(parent.kind, ()):
                explorer = TopExp_Explorer(parent.shape, enum_value)
                while explorer.More():
                    current = explorer.Current()
                    child = next(
                        (
                            candidate
                            for candidate in transient_index.get(
                                (child_kind, hash(current.Oriented(TopAbs_FORWARD))),
                                (),
                            )
                            if _same(current, candidate.shape)
                        ),
                        None,
                    )
                    if child is not None:
                        contains[parent.element_id].add(child.element_id)
                        contained_by[child.element_id].add(parent.element_id)
                        relation_links += 1
                        if relation_links > MAX_RELATION_LINKS:
                            raise GeometryEvidenceError(
                                "Topology relation resource limit exceeded"
                            )
                    explorer.Next()

        adjacent: dict[str, set[str]] = defaultdict(set)
        connected: dict[str, set[str]] = defaultdict(set)
        kind_by_id = {item.element_id: item.kind for item in drafts}
        for kind, relation, via_kind in (
            ("FACE", adjacent, "EDGE"),
            ("EDGE", connected, "VERTEX"),
        ):
            items = [item for item in drafts if item.kind == kind]
            parents_by_child: dict[str, list[str]] = defaultdict(list)
            for item in items:
                for child_id in contains[item.element_id]:
                    if kind_by_id[child_id] == via_kind:
                        parents_by_child[child_id].append(item.element_id)
            for parent_ids in parents_by_child.values():
                for left_id, right_id in combinations(sorted(set(parent_ids)), 2):
                    relation[left_id].add(right_id)
                    relation[right_id].add(left_id)
                    relation_links += 2
                    if relation_links > MAX_RELATION_LINKS:
                        raise GeometryEvidenceError(
                            "Topology relation resource limit exceeded"
                        )
        return {
            item.element_id: {
                "contained_by": tuple(sorted(contained_by[item.element_id])),
                "contains": tuple(sorted(contains[item.element_id])),
                "adjacent_to": tuple(sorted(adjacent[item.element_id])),
                "connected_to": tuple(sorted(connected[item.element_id])),
            }
            for item in drafts
        }

    @staticmethod
    def _tolerance(shape: Any, kind: str) -> float:
        from OCP.BRep import BRep_Tool  # type: ignore[import-untyped]

        if kind in {"FACE", "EDGE", "VERTEX"}:
            return _rounded(BRep_Tool.Tolerance_s(shape))
        return 0.0

    @staticmethod
    def _limitations() -> tuple[str, ...]:
        return (
            "Evidence is geometric and does not infer manufacturing intent.",
            "Stable IDs are scoped to the declared kernel and stable-ID versions.",
            "Canonical ambiguity groups identify geometrically indistinguishable elements.",
            "Manufacturing tolerance is never inferred from kernel or modeling tolerance.",
            "No toolpath, postprocessor, executable CNC output or physical authority exists.",
            "All engineering use requires human review.",
        )
