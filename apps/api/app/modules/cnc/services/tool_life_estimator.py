"""Taylor tool-life estimates for analytical review only."""

import math
from typing import Literal

from app.modules.cnc.schemas import ToolLifeTaylorAuditPayload


ToolMaterialPair = Literal[
    "CARBIDE_P20_P30_CARBON_STEEL", "CARBIDE_K10_ALUMINUM_6061_T6"
]

_TAYLOR_PROFILES: dict[ToolMaterialPair, tuple[float, float]] = {
    "CARBIDE_P20_P30_CARBON_STEEL": (0.25, 350.0),
    "CARBIDE_K10_ALUMINUM_6061_T6": (0.30, 800.0),
}


def _positive_finite(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(code)
    return float(value)


def _nonnegative_finite(value: float, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(code)
    return float(value)


def _profile(material_reference: str) -> tuple[ToolMaterialPair, float, float]:
    if not isinstance(material_reference, str) or not material_reference.strip():
        raise ValueError("TAYLOR_MATERIAL_REFERENCE_INVALID")
    normalized = material_reference.upper()
    name: ToolMaterialPair | None = (
        "CARBIDE_K10_ALUMINUM_6061_T6"
        if "6061" in normalized
        else "CARBIDE_P20_P30_CARBON_STEEL"
        if any(code in normalized for code in ("1020", "1045", "CARBON"))
        else None
    )
    if name is None:
        raise ValueError("TAYLOR_TOOL_MATERIAL_PAIR_UNSUPPORTED")
    n_value, c_value = _TAYLOR_PROFILES[name]
    return name, n_value, c_value


def estimate_tool_life(
    tool_id: str,
    material_reference: str,
    *,
    cutting_speed_m_per_min: float,
    effective_cutting_time_minutes: float,
    taylor_n: float | None = None,
    taylor_c: float | None = None,
) -> ToolLifeTaylorAuditPayload:
    """Apply Vc*T^n=C and account for this plan's effective cutting time."""
    if not isinstance(tool_id, str) or not tool_id.strip():
        raise ValueError("TAYLOR_TOOL_REQUIRED")
    profile, default_n, default_c = _profile(material_reference)
    speed = _positive_finite(cutting_speed_m_per_min, code="TAYLOR_CUTTING_SPEED_INVALID")
    cutting_time = _nonnegative_finite(
        effective_cutting_time_minutes, code="TAYLOR_CUTTING_TIME_INVALID"
    )
    n_value = default_n if taylor_n is None else _positive_finite(taylor_n, code="TAYLOR_N_INVALID")
    c_value = default_c if taylor_c is None else _positive_finite(taylor_c, code="TAYLOR_C_INVALID")
    if n_value >= 1:
        raise ValueError("TAYLOR_N_INVALID")
    life = (c_value / speed) ** (1.0 / n_value)
    consumed = cutting_time / life * 100.0
    if not math.isfinite(life) or life <= 0 or not math.isfinite(consumed):
        raise ValueError("TAYLOR_ESTIMATE_NON_CONVERGENT")
    rounded_consumed = round(consumed, 9)
    return ToolLifeTaylorAuditPayload(
        tool_id=tool_id.strip(),
        tool_material_pair=profile,
        cutting_speed_vc_m_per_min=speed,
        taylor_n=n_value,
        taylor_c=c_value,
        effective_cutting_time_minutes=cutting_time,
        estimated_tool_life_minutes=round(life, 9),
        tool_life_consumed_percent=rounded_consumed,
        integrity_status=(
            "TOOL_LIFE_SAFE" if rounded_consumed <= 80.0 else "TOOL_LIFE_EXHAUSTED_WARNING"
        ),
    )


__all__ = ("estimate_tool_life",)
