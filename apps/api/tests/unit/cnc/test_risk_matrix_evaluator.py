import pytest
from pydantic import ValidationError

from app.modules.cam.schemas import TurningBoundingBox
from app.modules.cnc.schemas import (
    ChuckProximityAudit,
    MachiningRiskMatrixPayload,
    ToolpathSegment2D,
)
from app.modules.cnc.services.geometry_auditor import audit_geometry_dimensions
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force
from app.modules.cnc.services.risk_matrix_evaluator import evaluate_operational_risk
from app.modules.cnc.services.stability_auditor import audit_machining_stability
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


def _geometry(*, programmed_radius_mm: float = 25.0):
    return audit_geometry_dimensions(
        TurningBoundingBox(
            max_radius_mm=25.0,
            min_z_mm=-100.0,
            max_z_mm=0.0,
            total_z_length_mm=100.0,
        ),
        (
            ToolpathSegment2D(
                motion_type="RAPID",
                x_start_mm=programmed_radius_mm * 2,
                z_start_mm=0.0,
                x_end_mm=programmed_radius_mm * 2,
                z_end_mm=-100.0,
                active_tool="T0101",
            ),
        ),
        tolerance_mm=0.001,
    )


def _power(*, limit_kw: float = 7.5):
    return estimate_cutting_power_force(
        "Aço ABNT 1045",
        feed_mm_per_rev=0.2,
        depth_of_cut_mm=2.0,
        cutting_edge_angle_deg=95.0,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=1_500.0,
        max_spindle_rpm=3_000.0,
        machine_power_limit_kw=limit_kw,
    )


def _stability(*, overhang_mm: float = 60.0):
    return audit_machining_stability(
        tool_id="T0101",
        tool_overhang_mm=overhang_mm,
        tool_diameter_mm=20.0,
        young_modulus_mpa=210_000.0,
        cutting_force_n=1_000.0,
        specific_cutting_pressure_n_per_mm2=1_900.0,
        frf_real_compliance_mm_per_n=0.0002,
        depth_of_cut_mm=0.1,
    )


def _life(*, cutting_time_minutes: float = 2.0):
    return estimate_tool_life(
        "T0101",
        "Aço ABNT 1045",
        cutting_speed_m_per_min=180.0,
        effective_cutting_time_minutes=cutting_time_minutes,
    )


def _evaluate(
    *,
    radius: float = 25.0,
    clearance: float = 12.0,
    overhang: float = 60.0,
    power_limit: float = 7.5,
    cutting_time: float = 2.0,
    envelope: str = "PASS_DECLARED_2D_ENVELOPE_ONLY",
):
    return evaluate_operational_risk(
        envelope_audit=envelope,  # type: ignore[arg-type]
        geometry_audit=_geometry(programmed_radius_mm=radius),
        chuck_proximity=ChuckProximityAudit(
            minimum_clearance_mm=clearance,
            threshold_mm=5.0,
            closest_segment_index=0,
            warning_code="WARNING_PROXIMITY_CHUCK" if clearance < 5 else None,
        ),
        stability_audits=(_stability(overhang_mm=overhang),),
        power_force_audit=_power(limit_kw=power_limit),
        tool_life_audits=(_life(cutting_time_minutes=cutting_time),),
    )


def test_safe_snapshots_produce_low_risk_and_human_review_recommendation():
    result = _evaluate()
    assert result.overall_risk_score == 0
    assert result.risk_level == "LOW_RISK"
    assert result.dimensional_risk_score == 0
    assert result.dynamic_risk_score == 0
    assert result.energy_risk_score == 0
    assert result.tool_wear_risk_score == 0
    assert result.mitigation_recommendations == (
        "Manter revisão humana e homologação de processo antes de qualquer aplicação física.",
    )
    assert result.physical_use_authorized is False
    assert result.safety_flags.executable_output is False


@pytest.mark.parametrize(
    ("updates", "category", "score"),
    (
        ({"clearance": 4.0}, "dimensional_risk_score", 75.0),
        ({"overhang": 100.0}, "dynamic_risk_score", 75.0),
        ({"power_limit": 0.1}, "energy_risk_score", 75.0),
        ({"cutting_time": 20.0}, "tool_wear_risk_score", 75.0),
    ),
)
def test_each_analytical_warning_contributes_its_weighted_category(
    updates, category, score
):
    result = _evaluate(**updates)
    assert getattr(result, category) == score
    assert result.risk_level == "MODERATE_RISK"


def test_combined_dynamic_energy_and_wear_findings_require_mitigation():
    result = _evaluate(overhang=100.0, power_limit=0.1, cutting_time=20.0)
    assert result.overall_risk_score == 48.75
    assert result.risk_level == "HIGH_RISK_REQUIRES_MITIGATION"
    assert len(result.mitigation_recommendations) == 3


@pytest.mark.parametrize(
    "updates",
    (
        {"radius": 26.0},
        {"clearance": 0.0},
        {"envelope": "ENVELOPE_VIOLATION_DETECTED"},
    ),
)
def test_cinematic_or_collision_violation_is_compulsorily_critical(updates):
    result = _evaluate(**updates)
    assert result.dimensional_risk_score == 100
    assert result.risk_level == "CRITICAL_INTERVENTION_MANDATORY"
    assert result.mitigation_recommendations[0].startswith("Interromper")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("overall_risk_score", 99.0),
        ("dynamic_risk_score", 75.0),
        ("risk_level", "CRITICAL_INTERVENTION_MANDATORY"),
        ("mitigation_recommendations", ("ignorar riscos",)),
    ),
)
def test_contract_rejects_tampered_score_level_or_recommendation(field, value):
    body = _evaluate().model_dump()
    body[field] = value
    with pytest.raises(ValidationError):
        MachiningRiskMatrixPayload.model_validate(body)


def test_evaluator_requires_source_snapshots_and_rejects_promoted_authority():
    with pytest.raises(ValueError, match="RISK_MATRIX_STABILITY_AUDIT_REQUIRED"):
        evaluate_operational_risk(
            envelope_audit="PASS_DECLARED_2D_ENVELOPE_ONLY",
            geometry_audit=_geometry(),
            chuck_proximity=ChuckProximityAudit(
                minimum_clearance_mm=12.0,
                threshold_mm=5.0,
                closest_segment_index=0,
            ),
            stability_audits=(),
            power_force_audit=_power(),
            tool_life_audits=(_life(),),
        )

    body = _evaluate().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        MachiningRiskMatrixPayload.model_validate(body)
