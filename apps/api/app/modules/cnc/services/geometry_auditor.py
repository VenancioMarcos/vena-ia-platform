"""Fail-closed dimensional audit between BRep bounds and programmed turning motion."""

from __future__ import annotations

import math
from typing import Literal, Sequence

from app.modules.cam.schemas import TurningBoundingBox
from app.modules.cnc.schemas import (
    DimensionalDeviation,
    GeometryDimensionalAuditReport,
    ToolpathSegment2D,
)


AuditAxis = Literal["MAX_RADIUS", "MIN_Z", "MAX_Z"]


class GeometryDimensionalAuditError(ValueError):
    """Rejected audit retaining the analytical deviation report for review."""

    def __init__(self, report: GeometryDimensionalAuditReport) -> None:
        self.report = report
        super().__init__(";".join(report.findings))


def _deviation(
    axis: AuditAxis,
    nominal_mm: float,
    programmed_mm: float,
    tolerance_mm: float,
) -> DimensionalDeviation:
    return DimensionalDeviation(
        axis=axis,
        nominal_mm=nominal_mm,
        programmed_mm=programmed_mm,
        signed_deviation_mm=programmed_mm - nominal_mm,
        tolerance_mm=tolerance_mm,
        within_tolerance=math.isclose(
            programmed_mm,
            nominal_mm,
            abs_tol=tolerance_mm,
            rel_tol=0,
        ),
    )


def audit_geometry_dimensions(
    source_brep_bounds: TurningBoundingBox,
    segments: Sequence[ToolpathSegment2D],
    *,
    tolerance_mm: float,
) -> GeometryDimensionalAuditReport:
    """Compare BRep nominal R/Z bounds with parsed X-diameter/Z motion extrema.

    The audit is analytical only. Any dimensional mismatch, negative radius or
    reversal of radial cutting direction closes the manifest-generation gate.
    """
    if (
        isinstance(tolerance_mm, bool)
        or not isinstance(tolerance_mm, (int, float))
        or not math.isfinite(tolerance_mm)
        or tolerance_mm <= 0
        or tolerance_mm > 1.0
    ):
        raise ValueError("DIMENSIONAL_AUDIT_TOLERANCE_INVALID")
    if not segments:
        raise ValueError("DIMENSIONAL_AUDIT_TOOLPATH_REQUIRED")

    bounds = TurningBoundingBox.model_validate(source_brep_bounds)
    validated = tuple(ToolpathSegment2D.model_validate(segment) for segment in segments)
    points = tuple(
        point
        for segment in validated
        for point in (
            (segment.x_start_mm / 2.0, segment.z_start_mm),
            (segment.x_end_mm / 2.0, segment.z_end_mm),
        )
    )
    radii = tuple(point[0] for point in points)
    axial = tuple(point[1] for point in points)

    findings: list[str] = []
    if any(radius < 0 for radius in radii):
        findings.append("NEGATIVE_RADIUS_CUT")

    radial_directions: list[int] = []
    for segment in validated:
        if segment.motion_type != "LINEAR":
            continue
        radial_delta = (segment.x_end_mm - segment.x_start_mm) / 2.0
        if math.isclose(radial_delta, 0.0, abs_tol=tolerance_mm, rel_tol=0):
            continue
        radial_directions.append(1 if radial_delta > 0 else -1)
    if any(
        current != previous
        for previous, current in zip(radial_directions, radial_directions[1:])
    ):
        findings.append("UNSUPPORTED_DIAMETRAL_DIRECTION_REVERSAL")

    programmed_max_radius = max(radii)
    programmed_min_z = min(axial)
    programmed_max_z = max(axial)
    deviations = (
        _deviation(
            "MAX_RADIUS",
            bounds.max_radius_mm,
            programmed_max_radius,
            float(tolerance_mm),
        ),
        _deviation("MIN_Z", bounds.min_z_mm, programmed_min_z, float(tolerance_mm)),
        _deviation("MAX_Z", bounds.max_z_mm, programmed_max_z, float(tolerance_mm)),
    )
    findings.extend(
        f"BREP_{item.axis}_MISMATCH" for item in deviations if not item.within_tolerance
    )
    unique_findings = tuple(dict.fromkeys(findings))
    passed = not unique_findings
    return GeometryDimensionalAuditReport(
        status="PASS" if passed else "REJECTED",
        source_brep_bounds=bounds,
        programmed_min_radius_mm=min(radii),
        programmed_max_radius_mm=programmed_max_radius,
        programmed_min_z_mm=programmed_min_z,
        programmed_max_z_mm=programmed_max_z,
        deviations=deviations,
        findings=unique_findings,
        manifest_generation_allowed=passed,
    )


def require_geometry_dimensions_consistent(
    source_brep_bounds: TurningBoundingBox,
    segments: Sequence[ToolpathSegment2D],
    *,
    tolerance_mm: float,
) -> GeometryDimensionalAuditReport:
    """Return a passing report or fail closed while retaining rejection evidence."""
    report = audit_geometry_dimensions(
        source_brep_bounds,
        segments,
        tolerance_mm=tolerance_mm,
    )
    if report.status != "PASS":
        raise GeometryDimensionalAuditError(report)
    return report
