"""Ideal kinematic surface-roughness estimates for analytical review only."""

import math

from app.modules.cnc.schemas import SurfaceRoughnessAuditPayload


def _positive_finite(value: float, *, upper: float, code: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
        or value > upper
    ):
        raise ValueError(code)
    return float(value)


def estimate_surface_roughness(
    finish_feed_mm_per_rev: float,
    insert_nose_radius_mm: float,
    *,
    nominal_ra_max_um: float | None = None,
) -> SurfaceRoughnessAuditPayload:
    """Apply the ideal turning cusp equations; never represent measured roughness."""
    feed = _positive_finite(
        finish_feed_mm_per_rev,
        upper=5.0,
        code="SURFACE_ROUGHNESS_FEED_INVALID",
    )
    radius = _positive_finite(
        insert_nose_radius_mm,
        upper=10.0,
        code="SURFACE_ROUGHNESS_INSERT_RADIUS_INVALID",
    )
    nominal = (
        None
        if nominal_ra_max_um is None
        else _positive_finite(
            nominal_ra_max_um,
            upper=1_000.0,
            code="SURFACE_ROUGHNESS_NOMINAL_RA_INVALID",
        )
    )
    rz_um = feed**2 / (8.0 * radius) * 1_000.0
    ra_um = feed**2 / (32.0 * radius) * 1_000.0
    rounded_ra_um = round(ra_um, 9)
    rounded_rz_um = round(rz_um, 9)
    compliance = (
        "NOMINAL_RA_TOLERANCE_UNAVAILABLE"
        if nominal is None
        else (
            "WITHIN_NOMINAL_RA_TOLERANCE"
            if rounded_ra_um <= nominal
            else "EXCEEDS_NOMINAL_RA_TOLERANCE"
        )
    )
    return SurfaceRoughnessAuditPayload(
        ra_theoretical_um=rounded_ra_um,
        rz_theoretical_um=rounded_rz_um,
        finish_feed_mm_per_rev=feed,
        insert_nose_radius_mm=radius,
        nominal_ra_max_um=nominal,
        compliance_tag=compliance,
    )


__all__ = ("estimate_surface_roughness",)
