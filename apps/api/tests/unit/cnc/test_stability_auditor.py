import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import MachiningStabilityAuditPayload
from app.modules.cnc.services.stability_auditor import audit_machining_stability


def _audit(**updates: object) -> MachiningStabilityAuditPayload:
    values: dict[str, object] = {
        "tool_id": "T0101",
        "tool_overhang_mm": 60.0,
        "tool_diameter_mm": 20.0,
        "young_modulus_mpa": 210_000.0,
        "cutting_force_n": 1_000.0,
        "specific_cutting_pressure_n_per_mm2": 1_900.0,
        "frf_real_compliance_mm_per_n": 0.0002,
        "depth_of_cut_mm": 0.5,
    }
    values.update(updates)
    return audit_machining_stability(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("ratio", "expected_status"),
    [
        (3.0, "DYNAMICALLY_STABLE"),
        (5.0, "CHATTER_HIGH_RISK_WARNING"),
        (7.0, "CHATTER_HIGH_RISK_WARNING"),
    ],
)
def test_cantilever_math_and_overhang_status(ratio, expected_status):
    diameter = 20.0
    overhang = diameter * ratio
    audit = _audit(tool_overhang_mm=overhang, tool_diameter_mm=diameter)

    inertia = math.pi * diameter**4 / 64
    stiffness = 3 * 210_000 * inertia / overhang**3
    assert audit.overhang_ratio_l_d == pytest.approx(ratio)
    assert audit.second_moment_area_mm4 == pytest.approx(inertia)
    assert audit.equivalent_stiffness_n_per_mm == pytest.approx(stiffness)
    assert audit.static_deflection_um == pytest.approx(1_000 / stiffness * 1_000)
    assert audit.stability_limit_depth_mm == pytest.approx(1 / (2 * 1_900 * 0.0002))
    assert audit.stability_status == expected_status
    assert audit.physical_use_authorized is False
    assert audit.safety_flags.executable_output is False


def test_depth_above_analytical_limit_warns_even_with_short_overhang():
    audit = _audit(depth_of_cut_mm=2.0)
    assert audit.overhang_ratio_l_d == 3
    assert audit.stability_status == "CHATTER_HIGH_RISK_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tool_overhang_mm", 0, "STABILITY_TOOL_OVERHANG_INVALID"),
        ("tool_diameter_mm", -1, "STABILITY_TOOL_DIAMETER_INVALID"),
        ("young_modulus_mpa", 0, "STABILITY_YOUNG_MODULUS_INVALID"),
        ("cutting_force_n", float("nan"), "STABILITY_CUTTING_FORCE_INVALID"),
        (
            "specific_cutting_pressure_n_per_mm2",
            0,
            "STABILITY_SPECIFIC_CUTTING_PRESSURE_INVALID",
        ),
        ("frf_real_compliance_mm_per_n", 0, "STABILITY_FRF_COMPLIANCE_INVALID"),
        ("depth_of_cut_mm", -0.1, "STABILITY_DEPTH_OF_CUT_INVALID"),
    ],
)
def test_nonphysical_inputs_fail_closed(field, value, code):
    with pytest.raises(ValueError, match=code):
        _audit(**{field: value})


@pytest.mark.parametrize(
    "field",
    [
        "overhang_ratio_l_d",
        "second_moment_area_mm4",
        "equivalent_stiffness_n_per_mm",
        "static_deflection_um",
        "stability_limit_depth_mm",
    ],
)
def test_contract_rejects_tampered_derived_values(field):
    body = _audit().model_dump()
    body[field] *= 2
    with pytest.raises(ValidationError):
        MachiningStabilityAuditPayload.model_validate(body)


def test_contract_rejects_promoted_physical_authority():
    body = _audit().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        MachiningStabilityAuditPayload.model_validate(body)
