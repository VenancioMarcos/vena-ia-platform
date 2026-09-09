import math
import sys
from decimal import Inexact, ROUND_DOWN, getcontext, localcontext

import pytest

from app.modules.engineering.turning_quantization import evaluate_diameter_quantization


@pytest.mark.parametrize("radius,places,diameter", [
    (10.0, 3, 20.0), (12.34526, 3, 24.691), (12.34524, 3, 24.69),
    (0.0625, 2, 0.13), (1.25, 1, 2.5), (0.0, 6, 0.0),
])
def test_numeric_rounding_and_signed_deviation(radius: float, places: int, diameter: float) -> None:
    report = evaluate_diameter_quantization(radius, places)
    assert report.programmed_x_diameter_mm == diameter
    assert report.reconstructed_radius_mm == diameter / 2.0
    assert report.radial_deviation_mm == diameter / 2.0 - radius
    assert not report.is_boundary_safe and report.boundary_status == "NOT_EVALUATED"
    assert report.limitations == ("NUMERICAL_QUANTIZATION_CHECK_ONLY",)
    assert report == evaluate_diameter_quantization(radius, places)


@pytest.mark.parametrize("places", [-1, 0, 7, 1000000, True, 3.0, "3"])
def test_precision_is_strict_and_bounded(places: object) -> None:
    with pytest.raises(ValueError, match="decimal_places"):
        evaluate_diameter_quantization(10.0, places)  # type: ignore[arg-type]


@pytest.mark.parametrize("radius", [-1.0, math.nan, math.inf, -math.inf, True, 10, "10"])
def test_radius_contract_is_strict(radius: object) -> None:
    with pytest.raises(ValueError, match="radius"):
        evaluate_diameter_quantization(radius)  # type: ignore[arg-type]


def test_binary_tie_and_neighbors_are_explicit() -> None:
    # 0.125 is exactly representable; exact tie rounds upward to 0.13.
    assert evaluate_diameter_quantization(0.0625, 2).programmed_x_diameter_mm == 0.13
    assert evaluate_diameter_quantization(math.nextafter(0.0625, 0.0), 2).programmed_x_diameter_mm == 0.12
    assert evaluate_diameter_quantization(math.nextafter(0.0625, math.inf), 2).programmed_x_diameter_mm == 0.13


def test_context_independence_and_no_global_side_effect() -> None:
    expected = evaluate_diameter_quantization(12.34526)
    with localcontext() as context:
        context.prec = 2
        context.rounding = ROUND_DOWN
        context.Emax = 2
        context.Emin = -2
        context.traps[Inexact] = True
        context.clear_flags()
        before = (context.prec, context.rounding, context.Emax, context.Emin,
                  dict(context.traps), dict(context.flags))
        assert evaluate_diameter_quantization(12.34526) == expected
        assert (getcontext().prec, getcontext().rounding, getcontext().Emax, getcontext().Emin,
                dict(getcontext().traps), dict(getcontext().flags)) == before


def test_extremes_and_positive_value_lost_to_resolution_fail_closed() -> None:
    with pytest.raises(ValueError, match="overflow"):
        evaluate_diameter_quantization(sys.float_info.max)
    with pytest.raises(ValueError, match="lost"):
        evaluate_diameter_quantization(math.nextafter(0.0, math.inf), 6)
    with pytest.raises(ValueError, match="lost"):
        evaluate_diameter_quantization(1e-8, 6)
    result = evaluate_diameter_quantization(sys.float_info.max / 2, 6)
    assert result.programmed_x_diameter_mm == sys.float_info.max
    assert result.radial_deviation_mm == 0.0
