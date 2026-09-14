import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import MachiningParameterOptimizationPayload
from app.modules.cnc.services.parameter_optimizer import optimize_cutting_parameters
from app.modules.cnc.services.stability_auditor import audit_machining_stability


def _stability(*, overhang: float = 60.0):
    return audit_machining_stability(
        tool_id="T0101",
        tool_overhang_mm=overhang,
        tool_diameter_mm=20.0,
        young_modulus_mpa=210_000.0,
        cutting_force_n=1_100.0,
        specific_cutting_pressure_n_per_mm2=1_900.0,
        frf_real_compliance_mm_per_n=0.0005,
        depth_of_cut_mm=0.5,
    )


def _optimize(**updates: object):
    values: dict[str, object] = {
        "tool_id": "T0101",
        "programmed_vc_m_min": 180.0,
        "programmed_feed_mm_rev": 0.2,
        "programmed_ap_mm": 0.5,
        "vc_min_m_min": 90.0,
        "vc_max_m_min": 225.0,
        "feed_min_mm_rev": 0.1,
        "feed_max_mm_rev": 0.25,
        "ap_min_mm": 0.25,
        "ap_max_mm": 0.625,
        "target_ra_um": 1.5625,
        "insert_nose_radius_mm": 0.8,
        "cutting_edge_angle_deg": 95.0,
        "machine_power_limit_kw": 7.5,
        "max_spindle_rpm": 3_000.0,
        "stability_audit": _stability(),
    }
    values.update(updates)
    return optimize_cutting_parameters("Aço ABNT 1045", **values)  # type: ignore[arg-type]


def test_optimizer_maximizes_mrr_within_power_finish_and_stability_constraints():
    result = _optimize()
    assert result.optimization_status == "OPTIMAL_TRADE_OFF_FOUND"
    assert result.recommended_vc_m_min == pytest.approx(225.0)
    assert result.recommended_feed_mm_rev == pytest.approx(0.2)
    assert result.recommended_ap_mm == pytest.approx(result.stability_limit_depth_mm)
    assert result.predicted_ra_um == pytest.approx(1.5625)
    assert result.predicted_motor_power_kw <= result.machine_power_limit_kw
    assert result.predicted_mrr_cm3_min == pytest.approx(
        result.recommended_vc_m_min
        * result.recommended_feed_mm_rev
        * result.recommended_ap_mm
    )
    assert result.predicted_tool_life_minutes > 0
    assert result.physical_use_authorized is False


@pytest.mark.parametrize(
    "updates",
    (
        {"target_ra_um": 0.01},
        {"machine_power_limit_kw": 0.01},
        {"stability_audit": _stability(overhang=100.0)},
    ),
)
def test_incompatible_constraints_fail_closed_without_recommendations(updates):
    result = _optimize(**updates)
    assert result.optimization_status == "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED"
    assert result.recommended_vc_m_min is None
    assert result.predicted_mrr_cm3_min is None


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("target_ra_um", 0),
        ("machine_power_limit_kw", -1),
        ("feed_max_mm_rev", float("nan")),
        ("vc_min_m_min", 200.0),
    ),
)
def test_invalid_inputs_are_rejected(field, value):
    with pytest.raises(ValueError):
        _optimize(**{field: value})


@pytest.mark.parametrize(
    "field",
    (
        "recommended_vc_m_min",
        "recommended_feed_mm_rev",
        "recommended_ap_mm",
        "predicted_mrr_cm3_min",
        "predicted_motor_power_kw",
        "predicted_ra_um",
        "predicted_tool_life_minutes",
    ),
)
def test_contract_rejects_tampered_recommendations(field):
    body = _optimize().model_dump()
    body[field] *= 0.9
    with pytest.raises(ValidationError):
        MachiningParameterOptimizationPayload.model_validate(body)


def test_contract_rejects_false_unfeasible_and_promoted_authority():
    body = _optimize().model_dump()
    for field in (
        "recommended_vc_m_min",
        "recommended_feed_mm_rev",
        "recommended_ap_mm",
        "predicted_mrr_cm3_min",
        "predicted_motor_power_kw",
        "predicted_ra_um",
        "predicted_tool_life_minutes",
    ):
        body[field] = None
    body["optimization_status"] = "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED"
    with pytest.raises(ValidationError, match="OPTIMIZATION_FALSE_UNFEASIBLE_STATUS"):
        MachiningParameterOptimizationPayload.model_validate(body)

    body = _optimize().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        MachiningParameterOptimizationPayload.model_validate(body)
