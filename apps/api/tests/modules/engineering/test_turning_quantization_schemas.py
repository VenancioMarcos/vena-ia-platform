from __future__ import annotations

import math
import sys

import pytest
from pydantic import ValidationError

from app.modules.engineering.turning_toolpath_schemas import TurningQuantizationReport


def _report(original: float = 12.34526, diameter: float = 24.691,
            **updates: object) -> TurningQuantizationReport:
    reconstructed = diameter / 2.0
    return TurningQuantizationReport.model_validate({
        "original_radius_mm": original, "programmed_x_diameter_mm": diameter,
        "reconstructed_radius_mm": reconstructed,
        "radial_deviation_mm": reconstructed - original, **updates,
    })


@pytest.mark.parametrize("original,diameter,sign", [(12.34526, 24.691, 1),
    (12.34526, 24.690, -1), (12.0, 24.0, 0), (0.0, 0.0, 0)])
def test_signed_numeric_reconstruction_without_boundary_authority(
    original: float, diameter: float, sign: int,
) -> None:
    report = _report(original, diameter)
    assert report.reconstructed_radius_mm == diameter / 2
    assert report.radial_deviation_mm == diameter / 2 - original
    assert (report.radial_deviation_mm > 0) - (report.radial_deviation_mm < 0) == sign
    assert not report.is_boundary_safe and report.boundary_status == "NOT_EVALUATED"
    assert report.limitations == ("NUMERICAL_QUANTIZATION_CHECK_ONLY",)
    assert TurningQuantizationReport.model_validate_json(report.model_dump_json()) == report
    assert report == _report(original, diameter)


@pytest.mark.parametrize("field", ["original_radius_mm", "programmed_x_diameter_mm",
                                   "reconstructed_radius_mm"])
def test_negative_radius_and_diameter_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        _report(**{field: -1.0})


@pytest.mark.parametrize("field,value", [
    ("original_radius_mm", math.nan), ("programmed_x_diameter_mm", math.inf),
    ("reconstructed_radius_mm", -math.inf), ("radial_deviation_mm", math.nan),
    ("programmed_x_diameter_mm", "24.691"), ("original_radius_mm", True),
])
def test_nonfinite_values_and_coercions_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        _report(**{field: value})


@pytest.mark.parametrize("updates", [
    {"is_boundary_safe": True}, {"boundary_status": "PASS"},
    {"limitations": ()}, {"limitations": ("NUMERICAL_QUANTIZATION_CHECK_ONLY", "extra")},
    {"physical_use_authorized": True},
])
def test_no_forged_safety_or_removed_limitations(updates: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _report(**updates)


def test_inconsistent_derived_values_rejected_without_epsilon() -> None:
    valid = _report()
    with pytest.raises(ValidationError):
        _report(reconstructed_radius_mm=math.nextafter(valid.reconstructed_radius_mm, math.inf))
    with pytest.raises(ValidationError):
        _report(radial_deviation_mm=math.nextafter(valid.radial_deviation_mm, math.inf))
    with pytest.raises(ValidationError):
        _report(radial_deviation_mm=-valid.radial_deviation_mm)
    with pytest.raises(ValidationError):
        _report(1e-200, 4e-200, radial_deviation_mm=0.0)


def test_subnormal_underflow_rejected_and_representable_subnormal_retained() -> None:
    smallest = math.nextafter(0.0, math.inf)
    with pytest.raises(ValidationError, match="underflowed"):
        _report(0.0, smallest)
    valid = _report(0.0, 2 * smallest)
    assert valid.reconstructed_radius_mm == smallest and valid.radial_deviation_mm == smallest
    extreme = _report(sys.float_info.max, sys.float_info.max)
    assert math.isfinite(extreme.radial_deviation_mm) and extreme.radial_deviation_mm < 0


def test_frozen_model_and_instance_revalidation() -> None:
    report = _report()
    with pytest.raises(ValidationError):
        report.radial_deviation_mm = 0.0
    forged = report.model_copy(update={"is_boundary_safe": True})
    with pytest.raises(ValidationError):
        TurningQuantizationReport.model_validate(forged)
    forged_number = report.model_copy(update={"radial_deviation_mm": 0.0})
    with pytest.raises(ValidationError):
        TurningQuantizationReport.model_validate(forged_number)
