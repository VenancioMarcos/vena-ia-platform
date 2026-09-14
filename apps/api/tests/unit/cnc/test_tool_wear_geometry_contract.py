import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ToolWearGeometryAuditPayload
from app.modules.cnc.services.tool_life_estimator import estimate_tool_life


def _payload(*, tolerance_um: float = 100.0) -> ToolWearGeometryAuditPayload:
    source = estimate_tool_life(
        "T0101",
        "Aço ABNT 1045",
        cutting_speed_m_per_min=180.0,
        effective_cutting_time_minutes=1.0,
    )
    wear = 0.3 * source.tool_life_consumed_percent / 100.0
    radial = wear * 1_000.0
    return ToolWearGeometryAuditPayload(
        source_tool_life_audit=source,
        nominal_nose_radius_mm=0.8,
        maximum_allowable_flank_wear_vb_mm=0.3,
        estimated_flank_wear_vb_mm=wear,
        flank_wear_progress_percent=source.tool_life_consumed_percent,
        effective_nose_radius_mm=0.8 - wear / 2.0,
        predicted_radial_deviation_um=radial,
        predicted_axial_deviation_um=wear * 500.0,
        geometry_tolerance_um=tolerance_um,
        audit_status=(
            "TOOL_WEAR_GEOMETRY_EXCEEDED_WARNING"
            if radial > tolerance_um
            else "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE"
        ),
    )


def test_v2_contract_replays_with_progressive_flank_wear() -> None:
    audit = _payload()
    assert audit.schema_version == "vena-ia.cnc-tool-wear-geometry-audit/v2"
    assert audit.estimated_flank_wear_vb_mm > 0
    assert audit.effective_nose_radius_mm < audit.nominal_nose_radius_mm
    assert audit.physical_use_authorized is False
    assert audit.compensation_authorized is False
    assert ToolWearGeometryAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_tight_tolerance_produces_warning() -> None:
    assert _payload(tolerance_um=1.0).audit_status == "TOOL_WEAR_GEOMETRY_EXCEEDED_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("estimated_flank_wear_vb_mm", 0.2, "TOOL_WEAR_VB_MAX_INCONSISTENT"),
        ("effective_nose_radius_mm", 0.7, "TOOL_WEAR_NOSE_RADIUS_INCONSISTENT"),
        ("predicted_radial_deviation_um", 1.0, "TOOL_WEAR_RADIAL_DEVIATION_INCONSISTENT"),
    ],
)
def test_derived_geometry_cannot_be_adulterated(field: str, value: float, code: str) -> None:
    body = _payload().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        ToolWearGeometryAuditPayload.model_validate(body)


def test_safety_or_compensation_cannot_be_promoted() -> None:
    body = _payload().model_dump()
    body["compensation_authorized"] = True
    with pytest.raises(ValidationError):
        ToolWearGeometryAuditPayload.model_validate(body)
