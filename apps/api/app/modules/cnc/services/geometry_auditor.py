"""Fail-closed dimensional audit between BRep bounds and programmed turning motion."""

from __future__ import annotations

import math
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.cam.schemas import TurningBoundingBox
from app.modules.cnc.schemas import GCodeSafetyFlags, ToolpathSegment2D


AuditStatus = Literal["PASS", "REJECTED"]
AuditAxis = Literal["MAX_RADIUS", "MIN_Z", "MAX_Z"]


class _GeometryAuditContract(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        revalidate_instances="always",
    )


class DimensionalDeviation(_GeometryAuditContract):
    axis: AuditAxis
    nominal_mm: float
    programmed_mm: float
    signed_deviation_mm: float
    tolerance_mm: float = Field(gt=0, le=1.0)
    within_tolerance: bool

    @model_validator(mode="after")
    def validate_calculation(self) -> DimensionalDeviation:
        expected = self.programmed_mm - self.nominal_mm
        if not math.isclose(
            self.signed_deviation_mm,
            expected,
            abs_tol=1e-12,
            rel_tol=1e-12,
        ):
            raise ValueError("DIMENSIONAL_DEVIATION_INCONSISTENT")
        expected_within = math.isclose(
            self.programmed_mm,
            self.nominal_mm,
            abs_tol=self.tolerance_mm,
            rel_tol=0,
        )
        if self.within_tolerance != expected_within:
            raise ValueError("DIMENSIONAL_TOLERANCE_RESULT_INCONSISTENT")
        return self


class GeometryDimensionalAuditReport(_GeometryAuditContract):
    schema_version: Literal["vena-ia.cnc-geometry-dimensional-audit/v1"] = (
        "vena-ia.cnc-geometry-dimensional-audit/v1"
    )
    status: AuditStatus
    source_brep_bounds: TurningBoundingBox
    programmed_min_radius_mm: float
    programmed_max_radius_mm: float
    programmed_min_z_mm: float
    programmed_max_z_mm: float
    deviations: tuple[DimensionalDeviation, DimensionalDeviation, DimensionalDeviation]
    findings: tuple[str, ...]
    manifest_generation_allowed: bool
    coordinate_convention: Literal["LATHE_X_DIAMETER_Z"] = "LATHE_X_DIAMETER_Z"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_outcome(self) -> GeometryDimensionalAuditReport:
        passed = not self.findings and all(item.within_tolerance for item in self.deviations)
        if (self.status == "PASS") != passed:
            raise ValueError("GEOMETRY_AUDIT_STATUS_INCONSISTENT")
        if self.manifest_generation_allowed != passed:
            raise ValueError("GEOMETRY_AUDIT_GATE_INCONSISTENT")
        return self


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
