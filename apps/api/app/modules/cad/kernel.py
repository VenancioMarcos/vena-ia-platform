from __future__ import annotations

import math
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.cad.evidence import GeometryTopologyEvidence
    from app.modules.cad.features import FeatureRecognitionResult, FeatureRecognizer


class GeometryKernelError(Exception):
    pass


@dataclass(frozen=True)
class KernelGeometry:
    bounding_box: tuple[tuple[float, float, float], tuple[float, float, float]]
    surface_area: float
    volume: float | None
    topology_valid: bool
    shape_type: str


class OpenCascadeGeometryKernel:
    name = "OpenCascade Technology"
    version = "7.9.3"
    binding = "cadquery-ocp==7.9.3.1.1"

    def analyze_step(self, content: bytes) -> KernelGeometry:
        geometry, _features = self.analyze_step_with_features(content)
        return geometry

    def analyze_step_with_features(
        self,
        content: bytes,
        recognizer: FeatureRecognizer | None = None,
        unit: str = "mm",
    ) -> tuple[KernelGeometry, FeatureRecognitionResult | None]:
        shape, geometry = self._load_step_shape(content)
        features = None if recognizer is None else recognizer.recognize(shape, geometry, unit)
        return geometry, features

    def analyze_step_with_evidence(
        self,
        content: bytes,
        recognizer: FeatureRecognizer | None = None,
        unit: str = "mm",
    ) -> tuple[
        KernelGeometry,
        FeatureRecognitionResult | None,
        GeometryTopologyEvidence,
        str | None,
    ]:
        from app.modules.cad.evidence import (
            GeometryEvidenceBuilder,
            GeometryEvidenceError,
            unavailable_evidence,
        )

        shape, geometry = self._load_step_shape(content)
        try:
            evidence = GeometryEvidenceBuilder().build(
                shape,
                geometry,
                content,
                unit,
                kernel=self.name,
                kernel_version=self.version,
                kernel_binding=self.binding,
            )
        except GeometryEvidenceError as exc:
            evidence = unavailable_evidence(
                content,
                unit,
                kernel=self.name,
                kernel_version=self.version,
                kernel_binding=self.binding,
                warning=str(exc),
            )
        feature_warning = None
        try:
            features = None if recognizer is None else recognizer.recognize(shape, geometry, unit)
        except GeometryKernelError as exc:
            features = None
            feature_warning = str(exc)
        return geometry, features, evidence, feature_warning

    def _load_step_shape(self, content: bytes) -> tuple[object, KernelGeometry]:
        if len(content) > 50 * 1024 * 1024:
            raise GeometryKernelError("STEP resource limit exceeded")
        if not content.lstrip().startswith(b"ISO-10303-21;"):
            raise GeometryKernelError("Invalid STEP Part 21 signature")
        try:
            from OCP.Bnd import Bnd_Box  # type: ignore[import-untyped]
            from OCP.BRepBndLib import BRepBndLib  # type: ignore[import-untyped]
            from OCP.BRepCheck import BRepCheck_Analyzer  # type: ignore[import-untyped]
            from OCP.BRepGProp import BRepGProp  # type: ignore[import-untyped]
            from OCP.GProp import GProp_GProps  # type: ignore[import-untyped]
            from OCP.IFSelect import IFSelect_RetDone  # type: ignore[import-untyped]
            from OCP.STEPControl import STEPControl_Reader  # type: ignore[import-untyped]
            from OCP.TopAbs import TopAbs_ShapeEnum  # type: ignore[import-untyped]
        except ImportError as exc:
            raise GeometryKernelError("Geometry kernel unavailable") from exc

        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as handle:
                handle.write(content)
                path = Path(handle.name)
            reader = STEPControl_Reader()
            if reader.ReadFile(str(path)) != IFSelect_RetDone:
                raise GeometryKernelError("STEP geometry read failed")
            if reader.TransferRoots() <= 0:
                raise GeometryKernelError("STEP contains no transferable geometry")
            shape = reader.OneShape()
            box = Bnd_Box()
            BRepBndLib.Add_s(shape, box)
            xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
            surface = GProp_GProps()
            BRepGProp.SurfaceProperties_s(shape, surface)
            area = surface.Mass()
            volume_props = GProp_GProps()
            BRepGProp.VolumeProperties_s(shape, volume_props)
            raw_volume = volume_props.Mass()
            shape_type = TopAbs_ShapeEnum(shape.ShapeType()).name.removeprefix("TopAbs_")
            valid = bool(BRepCheck_Analyzer(shape).IsValid())
            volume = (
                raw_volume if valid and shape_type in {"SOLID", "COMPSOLID", "COMPOUND"} else None
            )
            values = (xmin, ymin, zmin, xmax, ymax, zmax, area, raw_volume)
            if not all(math.isfinite(value) for value in values):
                raise GeometryKernelError("Non-finite geometry result")
            geometry = KernelGeometry(
                bounding_box=((xmin, ymin, zmin), (xmax, ymax, zmax)),
                surface_area=area,
                volume=volume,
                topology_valid=valid,
                shape_type=shape_type,
            )
            return shape, geometry
        except GeometryKernelError:
            raise
        except Exception as exc:
            raise GeometryKernelError("STEP geometry analysis failed safely") from exc
        finally:
            if path is not None:
                path.unlink(missing_ok=True)
