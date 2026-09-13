"""Kienzle cutting-force and power estimates for analytical review only."""

from dataclasses import dataclass
import math
from typing import Literal

from app.modules.cnc.schemas import MachiningPowerForceAuditPayload


MaterialProfile = Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]


@dataclass(frozen=True)
class _MaterialParameters:
    profile: MaterialProfile
    kc1_1_n_per_mm2: float
    exponent_mc: float


_MATERIALS = {
    "AISI_1020": _MaterialParameters("AISI_1020", 1_780.0, 0.25),
    "ABNT_1045": _MaterialParameters("ABNT_1045", 1_900.0, 0.26),
    "ALUMINUM_6061_T6": _MaterialParameters("ALUMINUM_6061_T6", 700.0, 0.23),
}


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


def _material_parameters(reference: str) -> _MaterialParameters:
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("MACHINING_MATERIAL_REFERENCE_INVALID")
    normalized = reference.upper().replace("Í", "I").replace("Ç", "C")
    if "6061" in normalized:
        return _MATERIALS["ALUMINUM_6061_T6"]
    if "1045" in normalized:
        return _MATERIALS["ABNT_1045"]
    if "1020" in normalized:
        return _MATERIALS["AISI_1020"]
    raise ValueError("MACHINING_MATERIAL_UNSUPPORTED")


def estimate_cutting_power_force(
    material_reference: str,
    *,
    feed_mm_per_rev: float,
    depth_of_cut_mm: float,
    cutting_edge_angle_deg: float,
    cutting_speed_m_per_min: float,
    spindle_rpm_reference: float,
    max_spindle_rpm: float,
    machine_power_limit_kw: float,
) -> MachiningPowerForceAuditPayload:
    """Apply the analytical Kienzle model without implying physical validation."""
    material = _material_parameters(material_reference)
    feed = _positive_finite(feed_mm_per_rev, upper=5.0, code="KIENZLE_FEED_INVALID")
    depth = _positive_finite(depth_of_cut_mm, upper=100.0, code="KIENZLE_DEPTH_INVALID")
    angle = _positive_finite(
        cutting_edge_angle_deg, upper=179.0, code="KIENZLE_CUTTING_EDGE_ANGLE_INVALID"
    )
    speed = _positive_finite(
        cutting_speed_m_per_min, upper=3_000.0, code="KIENZLE_CUTTING_SPEED_INVALID"
    )
    rpm_limit = _positive_finite(
        max_spindle_rpm, upper=30_000.0, code="KIENZLE_SPINDLE_LIMIT_INVALID"
    )
    rpm = _positive_finite(
        spindle_rpm_reference, upper=30_000.0, code="KIENZLE_SPINDLE_RPM_INVALID"
    )
    if rpm > rpm_limit:
        raise ValueError("KIENZLE_SPINDLE_RPM_EXCEEDS_LIMIT")
    power_limit = _positive_finite(
        machine_power_limit_kw, upper=1_000.0, code="KIENZLE_POWER_LIMIT_INVALID"
    )

    sin_kr = math.sin(math.radians(angle))
    if not math.isfinite(sin_kr) or sin_kr <= 0:
        raise ValueError("KIENZLE_CUTTING_EDGE_ANGLE_INVALID")
    chip_width = depth / sin_kr
    chip_thickness = feed * sin_kr
    if not math.isfinite(chip_width) or not math.isfinite(chip_thickness) or chip_thickness <= 0:
        raise ValueError("KIENZLE_CHIP_GEOMETRY_NON_CONVERGENT")

    force = material.kc1_1_n_per_mm2 * chip_width * chip_thickness ** (
        1.0 - material.exponent_mc
    )
    cutting_power = force * speed / (60.0 * 1_000.0)
    motor_power = cutting_power / 0.80
    mrr = speed * depth * feed
    if not all(math.isfinite(value) and value > 0 for value in (force, cutting_power, motor_power, mrr)):
        raise ValueError("KIENZLE_ESTIMATE_NON_CONVERGENT")

    rounded_motor_power = round(motor_power, 9)
    return MachiningPowerForceAuditPayload(
        material_profile=material.profile,
        kc1_1_n_per_mm2=material.kc1_1_n_per_mm2,
        kienzle_exponent_mc=material.exponent_mc,
        feed_mm_per_rev=feed,
        depth_of_cut_mm=depth,
        cutting_edge_angle_deg=angle,
        chip_thickness_mm=round(chip_thickness, 9),
        chip_width_mm=round(chip_width, 9),
        cutting_speed_m_per_min=speed,
        spindle_rpm_reference=rpm,
        max_spindle_rpm=rpm_limit,
        fc_nominal_n=round(force, 9),
        pc_cutting_kw=round(cutting_power, 9),
        p_motor_est_kw=rounded_motor_power,
        mrr_cm3_min=round(mrr, 9),
        machine_power_limit_kw=power_limit,
        power_status=(
            "POWER_WITHIN_LIMITS"
            if rounded_motor_power <= power_limit
            else "POWER_EXCEEDED_WARNING"
        ),
    )


__all__ = ("estimate_cutting_power_force",)
