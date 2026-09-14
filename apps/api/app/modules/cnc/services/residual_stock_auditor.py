"""Analytical 2D residual-stock audit for in-process turning geometry."""

from dataclasses import dataclass
import math
from typing import Literal

from app.modules.cam.schemas import RzPoint, TurningStrategyPlanResponse
from app.modules.cnc.schemas import (
    MachiningResidualStockAuditPayload,
    ResidualStockSection,
)


class ResidualStockAuditError(ValueError):
    """Stable fail-closed reason for unsupported or inconsistent audit inputs."""


@dataclass(frozen=True)
class _NominalSpan:
    radius_mm: float
    front_z_mm: float
    rear_z_mm: float


def _nominal_spans(profile: tuple[RzPoint, ...], tolerance_mm: float) -> tuple[_NominalSpan, ...]:
    spans = [
        _NominalSpan(
            radius_mm=first.r_mm,
            front_z_mm=max(first.z_mm, second.z_mm),
            rear_z_mm=min(first.z_mm, second.z_mm),
        )
        for first, second in zip(profile, profile[1:])
        if first.r_mm > tolerance_mm
        and math.isclose(first.r_mm, second.r_mm, abs_tol=tolerance_mm, rel_tol=0)
        and abs(first.z_mm - second.z_mm) > tolerance_mm
    ]
    spans.sort(key=lambda item: (-item.front_z_mm, -item.rear_z_mm))
    if not spans:
        raise ResidualStockAuditError("RESIDUAL_STOCK_PROFILE_WITHOUT_AXIAL_SPANS")
    for current, following in zip(spans, spans[1:]):
        if not math.isclose(
            current.rear_z_mm,
            following.front_z_mm,
            abs_tol=tolerance_mm,
            rel_tol=0,
        ):
            raise ResidualStockAuditError("RESIDUAL_STOCK_PROFILE_SPANS_DISCONTINUOUS")
    return tuple(spans)


def _radius_reached_at_z(
    plan: TurningStrategyPlanResponse,
    *,
    z_mm: float,
    stock_radius_mm: float,
    tolerance_mm: float,
) -> float:
    reached = [stock_radius_mm]
    for machining_pass in plan.passes:
        for first, second in zip(
            machining_pass.coordinates_rz_mm,
            machining_pass.coordinates_rz_mm[1:],
        ):
            delta_z = second.z_mm - first.z_mm
            if abs(delta_z) <= tolerance_mm:
                continue
            segment_min_z = min(first.z_mm, second.z_mm)
            segment_max_z = max(first.z_mm, second.z_mm)
            if z_mm < segment_min_z - tolerance_mm or z_mm > segment_max_z + tolerance_mm:
                continue
            fraction = (z_mm - first.z_mm) / delta_z
            reached.append(first.r_mm + fraction * (second.r_mm - first.r_mm))
    return min(reached)


def audit_residual_stock(
    *,
    source_plan_id: str,
    cam_plan: TurningStrategyPlanResponse,
    nominal_profile: tuple[RzPoint, ...],
    stock_radius_mm: float,
    finish_allowance_nominal_mm: float,
    linear_tolerance_mm: float,
    tool_cutting_edge_length_mm: float,
) -> MachiningResidualStockAuditPayload:
    """Compare the reached CAM envelope with each nominal axial BRep section."""
    validated_plan = TurningStrategyPlanResponse.model_validate(cam_plan)
    validated_profile = tuple(RzPoint.model_validate(point) for point in nominal_profile)
    scalar_inputs = (
        stock_radius_mm,
        finish_allowance_nominal_mm,
        linear_tolerance_mm,
        tool_cutting_edge_length_mm,
    )
    if (
        not source_plan_id
        or not validated_profile
        or any(not math.isfinite(value) for value in scalar_inputs)
        or stock_radius_mm <= 0
        or finish_allowance_nominal_mm < 0
        or linear_tolerance_mm <= 0
        or tool_cutting_edge_length_mm <= 0
    ):
        raise ResidualStockAuditError("RESIDUAL_STOCK_INPUT_INVALID")
    if max(point.r_mm for point in validated_profile) > stock_radius_mm + linear_tolerance_mm:
        raise ResidualStockAuditError("RESIDUAL_STOCK_PROFILE_OUTSIDE_STOCK")

    spans = _nominal_spans(validated_profile, linear_tolerance_mm)
    if any(
        abs(current.radius_mm - following.radius_mm)
        > tool_cutting_edge_length_mm + linear_tolerance_mm
        for current, following in zip(spans, spans[1:])
    ):
        raise ResidualStockAuditError("RESIDUAL_STOCK_STEP_TOOL_INCOMPATIBLE")

    audited_sections: list[ResidualStockSection] = []
    for span in spans:
        in_process_radius = round(
            _radius_reached_at_z(
                validated_plan,
                z_mm=(span.front_z_mm + span.rear_z_mm) / 2.0,
                stock_radius_mm=stock_radius_mm,
                tolerance_mm=linear_tolerance_mm,
            ),
            9,
        )
        audited_sections.append(
            ResidualStockSection(
                front_z_mm=span.front_z_mm,
                rear_z_mm=span.rear_z_mm,
                nominal_radius_mm=span.radius_mm,
                in_process_radius_mm=in_process_radius,
                residual_stock_mm=round(in_process_radius - span.radius_mm, 9),
            )
        )
    sections = tuple(audited_sections)
    residuals = tuple(item.residual_stock_mm for item in sections)
    minimum = min(residuals)
    maximum = max(residuals)
    average = math.fsum(residuals) / len(residuals)
    gouging = minimum < 0
    status: Literal[
        "UNIFORM_ALLOWANCE_COMPLIANT",
        "EXCESS_MATERIAL_DETECTED",
        "CRITICAL_GOUGING_VIOLATION",
    ] = (
        "CRITICAL_GOUGING_VIOLATION"
        if gouging
        else "EXCESS_MATERIAL_DETECTED"
        if maximum > finish_allowance_nominal_mm + 0.05
        else "UNIFORM_ALLOWANCE_COMPLIANT"
    )
    return MachiningResidualStockAuditPayload(
        source_plan_id=source_plan_id,
        source_cam_plan=validated_plan,
        source_nominal_profile=validated_profile,
        stock_radius_mm=stock_radius_mm,
        finish_allowance_nominal_mm=finish_allowance_nominal_mm,
        linear_tolerance_mm=linear_tolerance_mm,
        tool_cutting_edge_length_mm=tool_cutting_edge_length_mm,
        sections=sections,
        max_residual_stock_mm=round(maximum, 9),
        min_residual_stock_mm=round(minimum, 9),
        average_stock_allowance_mm=round(average, 9),
        gouging_detected=gouging,
        status=status,
    )


__all__ = (
    "ResidualStockAuditError",
    "audit_residual_stock",
)
