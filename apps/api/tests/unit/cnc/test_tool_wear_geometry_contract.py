import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ToolWearGeometryAuditPayload
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life
from app.modules.cnc.services.tool_wear_geometry_auditor import audit_tool_wear_geometry


def _source():
    return estimate_tool_life(
        "T0101",
        "Aço ABNT 1045",
        cutting_speed_m_per_min=180.0,
        effective_cutting_time_minutes=1.0,
    )


def _audit(*, tolerance_um: float = 100.0) -> ToolWearGeometryAuditPayload:
    return audit_tool_wear_geometry(
        _source(),
        nominal_nose_radius_mm=0.8,
        maximum_allowable_flank_wear_vb_mm=0.3,
        clearance_angle_deg=7.0,
        position_angle_deg=95.0,
        geometry_tolerance_um=tolerance_um,
    )


def test_cnmg_geometry_uses_progressive_flank_wear_equations() -> None:
    audit = _audit()
    expected_vb = 0.3 * math.sqrt(audit.flank_wear_progress_percent / 100.0)
    expected_radial = expected_vb * math.tan(math.radians(7.0))
    expected_axial = expected_radial / math.tan(math.radians(85.0))

    assert audit.schema_version == "vena-ia.cnc-tool-wear-geometry-audit/v2"
    assert audit.estimated_flank_wear_vb_mm == pytest.approx(expected_vb)
    assert audit.predicted_radial_deviation_um == pytest.approx(expected_radial * 1_000)
    assert audit.predicted_axial_deviation_um == pytest.approx(expected_axial * 1_000)
    assert audit.effective_nose_radius_mm == pytest.approx(0.8 + expected_radial / 2)
    assert audit.position_angle_deg == 95.0
    assert audit.physical_use_authorized is False
    assert audit.compensation_authorized is False
    assert ToolWearGeometryAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_radial_deviation_over_half_tolerance_produces_warning() -> None:
    assert _audit(tolerance_um=1.0).audit_status == (
        "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING"
    )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("estimated_flank_wear_vb_mm", 0.2, "TOOL_WEAR_VB_MAX_INCONSISTENT"),
        ("effective_nose_radius_mm", 0.7, "TOOL_WEAR_NOSE_RADIUS_INCONSISTENT"),
        ("predicted_radial_deviation_um", 1.0, "TOOL_WEAR_RADIAL_DEVIATION_INCONSISTENT"),
    ],
)
def test_derived_geometry_cannot_be_adulterated(field: str, value: float, code: str) -> None:
    body = _audit().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        ToolWearGeometryAuditPayload.model_validate(body)


@pytest.mark.parametrize(
    ("argument", "value", "code"),
    [
        ("clearance_angle_deg", 0.0, "TOOL_WEAR_CLEARANCE_ANGLE_INVALID"),
        ("clearance_angle_deg", 90.0, "TOOL_WEAR_CLEARANCE_ANGLE_INVALID"),
        ("position_angle_deg", 0.0, "TOOL_WEAR_POSITION_ANGLE_INVALID"),
        ("position_angle_deg", 90.0, "TOOL_WEAR_POSITION_ANGLE_INVALID"),
        ("position_angle_deg", 180.0, "TOOL_WEAR_POSITION_ANGLE_INVALID"),
        ("geometry_tolerance_um", float("nan"), "TOOL_WEAR_GEOMETRY_INPUT_INVALID"),
        ("nominal_nose_radius_mm", -0.8, "TOOL_WEAR_GEOMETRY_INPUT_INVALID"),
    ],
)
def test_invalid_angles_and_geometry_fail_closed(
    argument: str, value: float, code: str
) -> None:
    arguments = {
        "nominal_nose_radius_mm": 0.8,
        "clearance_angle_deg": 7.0,
        "position_angle_deg": 95.0,
        "geometry_tolerance_um": 100.0,
    }
    arguments[argument] = value
    with pytest.raises(ValueError, match=code):
        audit_tool_wear_geometry(_source(), **arguments)


def test_safety_or_compensation_cannot_be_promoted() -> None:
    body = _audit().model_dump()
    body["compensation_authorized"] = True
    with pytest.raises(ValidationError):
        ToolWearGeometryAuditPayload.model_validate(body)
