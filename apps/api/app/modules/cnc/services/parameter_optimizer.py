"""Deterministic multicriteria cutting-parameter recommendations for review only."""

from math import isfinite, sqrt

from app.modules.cnc.schemas import (
    MachiningParameterOptimizationPayload,
    MachiningStabilityAuditPayload,
)
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.roughness_estimator import estimate_surface_roughness
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


def _positive(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    result = float(value)
    if not isfinite(result) or result <= 0:
        raise ValueError(code)
    return result


def optimize_cutting_parameters(
    material_reference: str,
    *,
    tool_id: str,
    programmed_vc_m_min: float,
    programmed_feed_mm_rev: float,
    programmed_ap_mm: float,
    vc_min_m_min: float,
    vc_max_m_min: float,
    feed_min_mm_rev: float,
    feed_max_mm_rev: float,
    ap_min_mm: float,
    ap_max_mm: float,
    target_ra_um: float,
    insert_nose_radius_mm: float,
    cutting_edge_angle_deg: float,
    machine_power_limit_kw: float,
    max_spindle_rpm: float,
    stability_audit: MachiningStabilityAuditPayload,
) -> MachiningParameterOptimizationPayload:
    """Maximize analytical MRR under power, finish, and simplified stability limits."""
    if not isinstance(tool_id, str) or not tool_id.strip() or stability_audit.tool_id != tool_id.strip():
        raise ValueError("OPTIMIZATION_TOOL_SOURCE_INVALID")
    values = {
        "programmed_vc_m_min": _positive(programmed_vc_m_min, code="OPTIMIZATION_VC_INVALID"),
        "programmed_feed_mm_rev": _positive(programmed_feed_mm_rev, code="OPTIMIZATION_FEED_INVALID"),
        "programmed_ap_mm": _positive(programmed_ap_mm, code="OPTIMIZATION_AP_INVALID"),
        "vc_min_m_min": _positive(vc_min_m_min, code="OPTIMIZATION_VC_RANGE_INVALID"),
        "vc_max_m_min": _positive(vc_max_m_min, code="OPTIMIZATION_VC_RANGE_INVALID"),
        "feed_min_mm_rev": _positive(feed_min_mm_rev, code="OPTIMIZATION_FEED_RANGE_INVALID"),
        "feed_max_mm_rev": _positive(feed_max_mm_rev, code="OPTIMIZATION_FEED_RANGE_INVALID"),
        "ap_min_mm": _positive(ap_min_mm, code="OPTIMIZATION_AP_RANGE_INVALID"),
        "ap_max_mm": _positive(ap_max_mm, code="OPTIMIZATION_AP_RANGE_INVALID"),
        "target_ra_um": _positive(target_ra_um, code="OPTIMIZATION_TARGET_RA_INVALID"),
        "insert_nose_radius_mm": _positive(
            insert_nose_radius_mm, code="OPTIMIZATION_INSERT_RADIUS_INVALID"
        ),
        "cutting_edge_angle_deg": _positive(
            cutting_edge_angle_deg, code="OPTIMIZATION_CUTTING_EDGE_ANGLE_INVALID"
        ),
        "machine_power_limit_kw": _positive(
            machine_power_limit_kw, code="OPTIMIZATION_POWER_LIMIT_INVALID"
        ),
    }
    spindle_limit = _positive(max_spindle_rpm, code="OPTIMIZATION_SPINDLE_LIMIT_INVALID")
    if values["cutting_edge_angle_deg"] >= 180 or not (
        values["vc_min_m_min"] <= values["programmed_vc_m_min"] <= values["vc_max_m_min"]
        and values["feed_min_mm_rev"]
        <= values["programmed_feed_mm_rev"]
        <= values["feed_max_mm_rev"]
        and values["ap_min_mm"] <= values["programmed_ap_mm"] <= values["ap_max_mm"]
    ):
        raise ValueError("OPTIMIZATION_ENVELOPE_INVALID")

    probe = estimate_cutting_power_force(
        material_reference,
        feed_mm_per_rev=values["programmed_feed_mm_rev"],
        depth_of_cut_mm=values["programmed_ap_mm"],
        cutting_edge_angle_deg=values["cutting_edge_angle_deg"],
        cutting_speed_m_per_min=values["programmed_vc_m_min"],
        spindle_rpm_reference=min(1.0, spindle_limit),
        max_spindle_rpm=spindle_limit,
        machine_power_limit_kw=values["machine_power_limit_kw"],
    )
    base = dict(
        tool_id=tool_id.strip(),
        material_profile=probe.material_profile,
        stability_limit_depth_mm=stability_audit.stability_limit_depth_mm,
        overhang_ratio_l_d=stability_audit.overhang_ratio_l_d,
        **values,
    )
    finish_feed_cap = sqrt(
        values["target_ra_um"] * 32 * values["insert_nose_radius_mm"] / 1_000
    )
    feed = min(values["feed_max_mm_rev"], finish_feed_cap)
    depth = min(values["ap_max_mm"], stability_audit.stability_limit_depth_mm)
    if (
        stability_audit.overhang_ratio_l_d > 4
        or feed < values["feed_min_mm_rev"]
        or depth < values["ap_min_mm"]
    ):
        return MachiningParameterOptimizationPayload.model_validate(
            {**base, "optimization_status": "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED"}
        )

    unit_speed_audit = estimate_cutting_power_force(
        material_reference,
        feed_mm_per_rev=feed,
        depth_of_cut_mm=depth,
        cutting_edge_angle_deg=values["cutting_edge_angle_deg"],
        cutting_speed_m_per_min=1.0,
        spindle_rpm_reference=min(1.0, spindle_limit),
        max_spindle_rpm=spindle_limit,
        machine_power_limit_kw=values["machine_power_limit_kw"],
    )
    vc = min(
        values["vc_max_m_min"],
        values["machine_power_limit_kw"] / unit_speed_audit.p_motor_est_kw,
    )
    if vc < values["vc_min_m_min"]:
        return MachiningParameterOptimizationPayload.model_validate(
            {**base, "optimization_status": "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED"}
        )
    power = estimate_cutting_power_force(
        material_reference,
        feed_mm_per_rev=feed,
        depth_of_cut_mm=depth,
        cutting_edge_angle_deg=values["cutting_edge_angle_deg"],
        cutting_speed_m_per_min=vc,
        spindle_rpm_reference=min(1.0, spindle_limit),
        max_spindle_rpm=spindle_limit,
        machine_power_limit_kw=values["machine_power_limit_kw"],
    )
    roughness = estimate_surface_roughness(
        feed, values["insert_nose_radius_mm"], nominal_ra_max_um=values["target_ra_um"]
    )
    life = estimate_tool_life(
        tool_id, material_reference, cutting_speed_m_per_min=vc, effective_cutting_time_minutes=0
    )
    return MachiningParameterOptimizationPayload.model_validate(
        {
            **base,
            "recommended_vc_m_min": round(vc, 9),
            "recommended_feed_mm_rev": round(feed, 9),
            "recommended_ap_mm": round(depth, 9),
            "predicted_mrr_cm3_min": power.mrr_cm3_min,
            "predicted_motor_power_kw": power.p_motor_est_kw,
            "predicted_ra_um": roughness.ra_theoretical_um,
            "predicted_tool_life_minutes": life.estimated_tool_life_minutes,
            "optimization_status": "OPTIMAL_TRADE_OFF_FOUND",
        }
    )


__all__ = ("optimize_cutting_parameters",)
