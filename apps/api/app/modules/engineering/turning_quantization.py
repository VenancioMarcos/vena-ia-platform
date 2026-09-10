"""Synthetic numeric diameter evaluation only; no NC text or boundary authority."""

import math
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from app.modules.engineering.turning_toolpath_schemas import (
    TurningChuckFixture, TurningMotionType, TurningOperationPlan,
    TurningPlanQuantizationSummary, TurningQuantizationReport, TurningStaticExclusionZone,
    TurningToolEnvelope2D, TurningToolpathMove, TurningToolpathPlan, TurningVerificationReport,
)

from app.modules.engineering.turning_verifier import verify_toolpath_boundaries


def evaluate_diameter_quantization(
    original_radius_mm: float, decimal_places: int = 3,
) -> TurningQuantizationReport:
    """Round the exact binary value of 2*R using decimal ROUND_HALF_UP.

    This policy is synthetic and explicitly differs from rounding an original
    user-entered decimal string. The return type contains floats, not NC tokens.
    """
    if type(decimal_places) is not int or not 1 <= decimal_places <= 6:
        raise ValueError("decimal_places must be an integer from 1 to 6")
    if type(original_radius_mm) is not float or not math.isfinite(original_radius_mm):
        raise ValueError("original radius must be a finite float")
    if original_radius_mm < 0:
        raise ValueError("original radius must be nonnegative")
    ideal = 2.0 * original_radius_mm
    if not math.isfinite(ideal):
        raise ValueError("diameter overflow")
    # 400 digits accommodate every finite float's integer part plus six decimals.
    # An explicit Context avoids inheriting caller precision, rounding or traps.
    with localcontext(Context(prec=400, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)):
        quantum = Decimal(1).scaleb(-decimal_places)
        quantized = Decimal.from_float(ideal).quantize(quantum, rounding=ROUND_HALF_UP)
        diameter = float(quantized)
    if not math.isfinite(diameter):
        raise ValueError("quantized diameter overflow")
    if ideal > 0.0 and diameter == 0.0:
        raise ValueError("positive diameter lost at requested resolution")
    radius = diameter / 2.0
    return TurningQuantizationReport(
        original_radius_mm=original_radius_mm, programmed_x_diameter_mm=diameter,
        reconstructed_radius_mm=radius, radial_deviation_mm=radius - original_radius_mm,
    )


def evaluate_plan_diameter_quantization(
    plan: TurningToolpathPlan, decimal_places: int = 3,
) -> TurningPlanQuantizationSummary:
    """Evaluate start/end radii in operation/move order, retaining shared endpoints."""
    if type(decimal_places) is not int or not 1 <= decimal_places <= 6:
        raise ValueError("decimal_places must be an integer from 1 to 6")
    validated = TurningToolpathPlan.model_validate(plan)
    reports = tuple(
        evaluate_diameter_quantization(point[0], decimal_places)
        for operation in validated.operations
        for move in operation.moves
        for point in (move.start_point, move.end_point)
    )
    return TurningPlanQuantizationSummary(
        decimal_places=decimal_places,
        evaluated_moves_count=sum(len(operation.moves) for operation in validated.operations),
        max_positive_radial_deviation_mm=max(
            0.0, max((r.radial_deviation_mm for r in reports), default=0.0),
        ),
        max_negative_radial_deviation_mm=min(
            0.0, min((r.radial_deviation_mm for r in reports), default=0.0),
        ),
        move_reports=reports,
    )


def reconstruct_quantized_toolpath_plan(
    plan: TurningToolpathPlan, decimal_places: int = 3,
) -> TurningToolpathPlan:
    """Reconstruct only radii; reject collapsed moves rather than dropping them."""
    validated = TurningToolpathPlan.model_validate(plan)
    summary = evaluate_plan_diameter_quantization(validated, decimal_places)
    endpoints = iter(summary.move_reports)
    operations = []
    for operation in validated.operations:
        moves = tuple(TurningToolpathMove(
            start_point=(next(endpoints).reconstructed_radius_mm, move.start_point[1]),
            end_point=(next(endpoints).reconstructed_radius_mm, move.end_point[1]),
            motion_type=move.motion_type, feed_rate_type=move.feed_rate_type,
        ) for move in operation.moves)
        operations.append(TurningOperationPlan(
            operation_id=operation.operation_id, operation_type=operation.operation_type,
            passes_count=operation.passes_count, moves=moves,
        ))
    length = math.fsum(math.dist(move.start_point, move.end_point)
                       for operation in operations for move in operation.moves
                       if move.motion_type == TurningMotionType.CUTTING)
    return TurningToolpathPlan(
        profile_id=validated.profile_id, operations=tuple(operations), total_cutting_length_mm=length,
    )


def verify_quantized_plan_boundaries(
    original_plan: TurningToolpathPlan, fixture: TurningChuckFixture,
    tool: TurningToolEnvelope2D, exclusion_zones: tuple[TurningStaticExclusionZone, ...],
    decimal_places: int = 3,
) -> tuple[TurningToolpathPlan, TurningVerificationReport]:
    """Check declared boundaries with quantized R and unchanged Z; no NC claim."""
    reconstructed = reconstruct_quantized_toolpath_plan(original_plan, decimal_places)
    report = verify_toolpath_boundaries(reconstructed, fixture, tool, exclusion_zones)
    return reconstructed, report
