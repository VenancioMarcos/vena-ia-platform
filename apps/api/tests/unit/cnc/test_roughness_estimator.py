import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import GCodeSafetyFlags, SurfaceRoughnessAuditPayload
from app.modules.cnc.services.roughness_estimator import estimate_surface_roughness


@pytest.mark.parametrize("radius_mm", [0.4, 0.8, 1.2])
def test_ideal_cusp_equations_for_standard_insert_radii(radius_mm: float) -> None:
    report = estimate_surface_roughness(0.2, radius_mm)

    assert report.ra_theoretical_um == pytest.approx(0.2**2 / (32 * radius_mm) * 1_000)
    assert report.rz_theoretical_um == pytest.approx(0.2**2 / (8 * radius_mm) * 1_000)
    assert report.rz_theoretical_um == pytest.approx(report.ra_theoretical_um * 4)
    assert report.compliance_tag == "NOMINAL_RA_TOLERANCE_UNAVAILABLE"
    assert report.safety_flags == GCodeSafetyFlags()
    assert SurfaceRoughnessAuditPayload.model_validate_json(report.model_dump_json()) == report


def test_nominal_ra_compliance_is_explicit() -> None:
    within = estimate_surface_roughness(0.1, 0.8, nominal_ra_max_um=1.0)
    exceeded = estimate_surface_roughness(0.2, 0.8, nominal_ra_max_um=1.0)

    assert within.compliance_tag == "WITHIN_NOMINAL_RA_TOLERANCE"
    assert exceeded.compliance_tag == "EXCEEDS_NOMINAL_RA_TOLERANCE"


@pytest.mark.parametrize("radius_mm", [0.0, -0.8, math.inf, math.nan, True])
def test_invalid_insert_radius_fails_closed(radius_mm: float) -> None:
    with pytest.raises(ValueError, match="SURFACE_ROUGHNESS_INSERT_RADIUS_INVALID"):
        estimate_surface_roughness(0.2, radius_mm)


@pytest.mark.parametrize("feed", [0.0, -0.2, math.inf, math.nan, True])
def test_invalid_feed_fails_closed(feed: float) -> None:
    with pytest.raises(ValueError, match="SURFACE_ROUGHNESS_FEED_INVALID"):
        estimate_surface_roughness(feed, 0.8)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("ra_theoretical_um", 99.0),
        ("rz_theoretical_um", 99.0),
        ("compliance_tag", "WITHIN_NOMINAL_RA_TOLERANCE"),
    ),
)
def test_forged_calculation_or_compliance_tag_is_rejected(field: str, value: object) -> None:
    body = estimate_surface_roughness(0.2, 0.8).model_dump()
    body[field] = value
    with pytest.raises(ValidationError):
        SurfaceRoughnessAuditPayload.model_validate(body)
