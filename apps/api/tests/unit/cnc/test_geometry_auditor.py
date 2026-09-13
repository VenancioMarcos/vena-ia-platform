from __future__ import annotations

import math
from typing import Literal

import pytest
from pydantic import ValidationError

from app.modules.cam.schemas import TurningBoundingBox
from app.modules.cnc.schemas import GCodeSafetyFlags, ToolpathSegment2D
from app.modules.cnc.services.geometry_auditor import (
    DimensionalDeviation,
    GeometryDimensionalAuditError,
    GeometryDimensionalAuditReport,
    audit_geometry_dimensions,
    require_geometry_dimensions_consistent,
)


def _bounds() -> TurningBoundingBox:
    return TurningBoundingBox(
        max_radius_mm=10.0,
        min_z_mm=-20.0,
        max_z_mm=0.0,
        total_z_length_mm=20.0,
    )


def _segment(
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    motion_type: Literal["RAPID", "LINEAR"] = "LINEAR",
) -> ToolpathSegment2D:
    return ToolpathSegment2D(
        motion_type=motion_type,
        x_start_mm=start[0],
        z_start_mm=start[1],
        x_end_mm=end[0],
        z_end_mm=end[1],
        feed=0.2 if motion_type == "LINEAR" else None,
        effective_feed_mm_min=200.0 if motion_type == "LINEAR" else None,
        active_tool="T01",
    )


def test_passes_exact_brep_and_programmed_extrema_deterministically() -> None:
    segments = (
        _segment((20.0, 0.0), (20.0, -20.0)),
        _segment((20.0, -20.0), (10.0, -20.0)),
    )
    report = audit_geometry_dimensions(_bounds(), segments, tolerance_mm=0.001)

    assert report == audit_geometry_dimensions(_bounds(), segments, tolerance_mm=0.001)
    assert report.status == "PASS"
    assert report.manifest_generation_allowed is True
    assert report.programmed_max_radius_mm == 10.0
    assert report.programmed_min_radius_mm == 5.0
    assert report.findings == ()
    assert report.safety_flags == GCodeSafetyFlags()
    assert GeometryDimensionalAuditReport.model_validate_json(report.model_dump_json()) == report


def test_reports_each_signed_dimensional_deviation_fail_closed() -> None:
    report = audit_geometry_dimensions(
        _bounds(),
        (_segment((22.0, 1.0), (22.0, -21.0)),),
        tolerance_mm=0.01,
    )

    assert report.status == "REJECTED"
    assert report.manifest_generation_allowed is False
    assert report.findings == (
        "BREP_MAX_RADIUS_MISMATCH",
        "BREP_MIN_Z_MISMATCH",
        "BREP_MAX_Z_MISMATCH",
    )
    assert tuple(item.signed_deviation_mm for item in report.deviations) == (1.0, -1.0, 1.0)


def test_negative_programmed_radius_is_rejected() -> None:
    report = audit_geometry_dimensions(
        _bounds(),
        (_segment((-2.0, 0.0), (-2.0, -20.0)), _segment((-2.0, -20.0), (20.0, -20.0))),
        tolerance_mm=0.001,
    )
    assert report.status == "REJECTED"
    assert "NEGATIVE_RADIUS_CUT" in report.findings


def test_reversing_linear_radial_direction_is_rejected() -> None:
    report = audit_geometry_dimensions(
        _bounds(),
        (
            _segment((20.0, 0.0), (10.0, 0.0)),
            _segment((10.0, 0.0), (20.0, -20.0)),
        ),
        tolerance_mm=0.001,
    )
    assert "UNSUPPORTED_DIAMETRAL_DIRECTION_REVERSAL" in report.findings
    assert report.manifest_generation_allowed is False


def test_rapid_retraction_does_not_create_cutting_direction_reversal() -> None:
    report = audit_geometry_dimensions(
        _bounds(),
        (
            _segment((20.0, 0.0), (10.0, -20.0)),
            _segment((10.0, -20.0), (20.0, -20.0), motion_type="RAPID"),
        ),
        tolerance_mm=0.001,
    )
    assert report.status == "PASS"


def test_require_gate_raises_with_analytical_report() -> None:
    with pytest.raises(GeometryDimensionalAuditError) as captured:
        require_geometry_dimensions_consistent(
            _bounds(),
            (_segment((22.0, 0.0), (22.0, -20.0)),),
            tolerance_mm=0.001,
        )
    assert captured.value.report.status == "REJECTED"
    assert captured.value.report.manifest_generation_allowed is False


@pytest.mark.parametrize("tolerance", [0.0, -0.1, 1.1, math.nan, math.inf, True])
def test_rejects_invalid_tolerance(tolerance: object) -> None:
    with pytest.raises(ValueError, match="DIMENSIONAL_AUDIT_TOLERANCE_INVALID"):
        audit_geometry_dimensions(
            _bounds(),
            (_segment((20.0, 0.0), (20.0, -20.0)),),
            tolerance_mm=tolerance,  # type: ignore[arg-type]
        )


def test_rejects_empty_toolpath() -> None:
    with pytest.raises(ValueError, match="DIMENSIONAL_AUDIT_TOOLPATH_REQUIRED"):
        audit_geometry_dimensions(_bounds(), (), tolerance_mm=0.001)


def test_report_contract_rejects_forged_gate_and_deviation() -> None:
    deviation = DimensionalDeviation(
        axis="MAX_RADIUS",
        nominal_mm=10.0,
        programmed_mm=10.0,
        signed_deviation_mm=0.0,
        tolerance_mm=0.001,
        within_tolerance=True,
    )
    body = {
        "status": "PASS",
        "source_brep_bounds": _bounds(),
        "programmed_min_radius_mm": 5.0,
        "programmed_max_radius_mm": 10.0,
        "programmed_min_z_mm": -20.0,
        "programmed_max_z_mm": 0.0,
        "deviations": (deviation, deviation, deviation),
        "findings": (),
        "manifest_generation_allowed": False,
    }
    with pytest.raises(ValidationError, match="GEOMETRY_AUDIT_GATE_INCONSISTENT"):
        GeometryDimensionalAuditReport.model_validate(body)
    with pytest.raises(ValidationError, match="DIMENSIONAL_DEVIATION_INCONSISTENT"):
        DimensionalDeviation(
            **(deviation.model_dump() | {"signed_deviation_mm": 1.0})
        )
