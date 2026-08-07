import math
from pathlib import Path

import pytest

from app.modules.cad.kernel import GeometryKernelError, OpenCascadeGeometryKernel


def _box_step(tmp_path: Path, x: float, y: float, z: float) -> bytes:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.IFSelect import IFSelect_RetDone

    path = tmp_path / "synthetic-box.step"
    writer = STEPControl_Writer()
    writer.Transfer(BRepPrimAPI_MakeBox(x, y, z).Shape(), STEPControl_AsIs)
    assert writer.Write(str(path)) == IFSelect_RetDone
    return path.read_bytes()


def test_real_kernel_box_reference(tmp_path: Path) -> None:
    result = OpenCascadeGeometryKernel().analyze_step(_box_step(tmp_path, 10, 20, 30))
    assert result.topology_valid is True
    assert result.shape_type in {"SOLID", "COMPOUND"}
    # OCCT expands Bnd_Box by its 1e-7 kernel gap on each boundary.
    assert result.bounding_box[0] == pytest.approx((0, 0, 0), abs=2e-7)
    assert result.bounding_box[1] == pytest.approx((10, 20, 30), abs=2e-7)
    assert result.surface_area == pytest.approx(2200, rel=1e-9)
    assert result.volume == pytest.approx(6000, rel=1e-9)
    assert math.isfinite(result.surface_area)


@pytest.mark.parametrize("content", [b"not-step", b"ISO-10303-21;\ntruncated", b""])
def test_kernel_fails_safe_for_malformed(content: bytes) -> None:
    with pytest.raises(GeometryKernelError):
        OpenCascadeGeometryKernel().analyze_step(content)
