"""Consolidated analytical CNC risk evaluation for human review only."""

from collections.abc import Sequence
from typing import Literal

from app.modules.cnc.schemas import (
    ChuckProximityAudit,
    GeometryDimensionalAuditReport,
    MachiningPowerForceAuditPayload,
    MachiningRiskMatrixPayload,
    MachiningStabilityAuditPayload,
    ToolLifeTaylorAuditPayload,
)


EnvelopeAudit = Literal[
    "PASS_DECLARED_2D_ENVELOPE_ONLY", "ENVELOPE_VIOLATION_DETECTED"
]
RiskLevel = Literal[
    "LOW_RISK",
    "MODERATE_RISK",
    "HIGH_RISK_REQUIRES_MITIGATION",
    "CRITICAL_INTERVENTION_MANDATORY",
]


def _recommendations(
    *,
    hard_dimensional_violation: bool,
    proximity_risk: bool,
    dynamic_risk: bool,
    energy_risk: bool,
    wear_risk: bool,
) -> tuple[str, ...]:
    items: list[str] = []
    if hard_dimensional_violation:
        items.append(
            "Interromper a avaliação do processo e revisar envelope, geometria e trajetória."
        )
    elif proximity_risk:
        items.append(
            "Revisar trajetória, origem e fixação para ampliar a folga em relação à placa."
        )
    if dynamic_risk:
        items.append(
            "Reduzir balanço ou profundidade de corte e revisar a rigidez antes da homologação."
        )
    if energy_risk:
        items.append("Reduzir a carga de corte e conferir a capacidade nominal da máquina.")
    if wear_risk:
        items.append("Planejar inspeção ou troca da aresta antes de qualquer aplicação física.")
    if not items:
        items.append(
            "Manter revisão humana e homologação de processo antes de qualquer aplicação física."
        )
    return tuple(items)


def evaluate_operational_risk(
    *,
    envelope_audit: EnvelopeAudit,
    geometry_audit: GeometryDimensionalAuditReport,
    chuck_proximity: ChuckProximityAudit,
    stability_audits: Sequence[MachiningStabilityAuditPayload],
    power_force_audit: MachiningPowerForceAuditPayload,
    tool_life_audits: Sequence[ToolLifeTaylorAuditPayload],
) -> MachiningRiskMatrixPayload:
    """Aggregate existing analytical findings without granting machine authority."""
    if not stability_audits:
        raise ValueError("RISK_MATRIX_STABILITY_AUDIT_REQUIRED")
    if not tool_life_audits:
        raise ValueError("RISK_MATRIX_TOOL_LIFE_AUDIT_REQUIRED")

    max_overhang_ratio = max(item.overhang_ratio_l_d for item in stability_audits)
    dynamic_warning = any(
        item.stability_status == "CHATTER_HIGH_RISK_WARNING" for item in stability_audits
    )
    max_tool_life_consumed = max(
        item.tool_life_consumed_percent for item in tool_life_audits
    )
    wear_warning = any(
        item.integrity_status == "TOOL_LIFE_EXHAUSTED_WARNING"
        for item in tool_life_audits
    )
    hard_dimensional_violation = (
        envelope_audit == "ENVELOPE_VIOLATION_DETECTED"
        or geometry_audit.status == "REJECTED"
        or not geometry_audit.manifest_generation_allowed
        or chuck_proximity.minimum_clearance_mm <= 0
    )
    proximity_risk = (
        chuck_proximity.warning_code == "WARNING_PROXIMITY_CHUCK"
        or chuck_proximity.minimum_clearance_mm < chuck_proximity.threshold_mm
    )
    dynamic_risk = dynamic_warning or max_overhang_ratio > 4
    energy_risk = (
        power_force_audit.power_status == "POWER_EXCEEDED_WARNING"
        or power_force_audit.p_motor_est_kw > power_force_audit.machine_power_limit_kw
    )
    wear_risk = wear_warning or max_tool_life_consumed > 80

    dimensional_score = (
        100.0 if hard_dimensional_violation else 75.0 if proximity_risk else 0.0
    )
    dynamic_score = 75.0 if dynamic_risk else 0.0
    energy_score = 75.0 if energy_risk else 0.0
    wear_score = 75.0 if wear_risk else 0.0
    overall_score = round(
        dimensional_score * 0.35
        + dynamic_score * 0.25
        + energy_score * 0.20
        + wear_score * 0.20,
        9,
    )
    risk_level: RiskLevel = (
        "CRITICAL_INTERVENTION_MANDATORY"
        if hard_dimensional_violation
        else "HIGH_RISK_REQUIRES_MITIGATION"
        if overall_score >= 40
        else "MODERATE_RISK"
        if overall_score >= 15
        else "LOW_RISK"
    )

    return MachiningRiskMatrixPayload(
        envelope_audit=envelope_audit,
        geometry_audit_status=geometry_audit.status,
        geometry_manifest_generation_allowed=geometry_audit.manifest_generation_allowed,
        minimum_chuck_clearance_mm=chuck_proximity.minimum_clearance_mm,
        chuck_proximity_threshold_mm=chuck_proximity.threshold_mm,
        chuck_proximity_warning=(
            chuck_proximity.warning_code == "WARNING_PROXIMITY_CHUCK"
        ),
        max_overhang_ratio_l_d=max_overhang_ratio,
        dynamic_warning_present=dynamic_warning,
        required_motor_power_kw=power_force_audit.p_motor_est_kw,
        machine_power_limit_kw=power_force_audit.machine_power_limit_kw,
        power_warning_present=(
            power_force_audit.power_status == "POWER_EXCEEDED_WARNING"
        ),
        max_tool_life_consumed_percent=max_tool_life_consumed,
        tool_wear_warning_present=wear_warning,
        overall_risk_score=overall_score,
        risk_level=risk_level,
        dimensional_risk_score=dimensional_score,
        dynamic_risk_score=dynamic_score,
        energy_risk_score=energy_score,
        tool_wear_risk_score=wear_score,
        mitigation_recommendations=_recommendations(
            hard_dimensional_violation=hard_dimensional_violation,
            proximity_risk=proximity_risk,
            dynamic_risk=dynamic_risk,
            energy_risk=energy_risk,
            wear_risk=wear_risk,
        ),
    )


__all__ = ("evaluate_operational_risk",)
