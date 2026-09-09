"""Synthetic numeric diameter evaluation only; no NC text or boundary authority."""

import math
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from app.modules.engineering.turning_toolpath_schemas import TurningQuantizationReport


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
