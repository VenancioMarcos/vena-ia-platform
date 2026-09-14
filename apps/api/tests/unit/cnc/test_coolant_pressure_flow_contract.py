import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import (
    CoolantPressureFlowAuditPayload,
    CoolantZoneRequirement,
)


def _requirements(mode: str) -> tuple[CoolantZoneRequirement, ...]:
    table = {
        "FLOOD": ((12.0, 4.0), (15.0, 6.0), (10.0, 3.0)),
        "MQL": ((0.05, 5.0), (0.08, 6.0), (0.04, 4.0)),
    }[mode]
    zones = (
        "PRIMARY_SHEAR_ZONE",
        "SECONDARY_TOOL_CHIP_INTERFACE",
        "TERTIARY_TOOL_WORKPIECE_INTERFACE",
    )
    return tuple(
        CoolantZoneRequirement(
            cutting_zone=zone,
            minimum_flow_l_per_min=limits[0],
            minimum_pressure_bar=limits[1],
        )
        for zone, limits in zip(zones, table, strict=True)
    )


def _payload(
    *,
    mode: str = "FLOOD",
    flow: float = 18.0,
    pressure: float = 8.0,
) -> CoolantPressureFlowAuditPayload:
    requirements = _requirements(mode)
    required_flow = max(item.minimum_flow_l_per_min for item in requirements)
    required_pressure = max(item.minimum_pressure_bar for item in requirements)
    return CoolantPressureFlowAuditPayload(
        coolant_mode=mode,
        programmed_flow_l_per_min=flow,
        programmed_pressure_bar=pressure,
        zone_requirements=requirements,
        minimum_required_flow_l_per_min=required_flow,
        minimum_required_pressure_bar=required_pressure,
        flow_margin_percent=(flow - required_flow) / required_flow * 100.0,
        pressure_margin_percent=(pressure - required_pressure) / required_pressure * 100.0,
        thermal_dissipation_status=(
            "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS"
            if flow >= required_flow and pressure >= required_pressure
            else "INSUFFICIENT_THERMAL_DISSIPATION_WARNING"
        ),
    )


@pytest.mark.parametrize(
    ("mode", "flow", "pressure"),
    [("FLOOD", 18.0, 8.0), ("MQL", 0.10, 7.0)],
)
def test_v2_contract_records_mode_zone_requirements_and_safe_margin(
    mode: str,
    flow: float,
    pressure: float,
) -> None:
    audit = _payload(mode=mode, flow=flow, pressure=pressure)
    assert audit.schema_version == "vena-ia.cnc-coolant-pressure-flow-audit/v2"
    assert audit.thermal_dissipation_status == (
        "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS"
    )
    assert audit.physical_use_authorized is False
    assert audit.automatic_coolant_control_authorized is False
    assert CoolantPressureFlowAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


@pytest.mark.parametrize(
    ("flow", "pressure"),
    [(10.0, 8.0), (18.0, 5.0), (10.0, 5.0)],
)
def test_insufficient_flow_or_pressure_warns_fail_closed(
    flow: float,
    pressure: float,
) -> None:
    assert _payload(flow=flow, pressure=pressure).thermal_dissipation_status == (
        "INSUFFICIENT_THERMAL_DISSIPATION_WARNING"
    )


def test_duplicate_or_tampered_zone_table_fails_closed() -> None:
    body = _payload().model_dump()
    body["zone_requirements"][0]["minimum_flow_l_per_min"] = 1.0
    with pytest.raises(ValidationError, match="COOLANT_ZONE_REQUIREMENTS_INCONSISTENT"):
        CoolantPressureFlowAuditPayload.model_validate(body)

    body = _payload().model_dump()
    body["zone_requirements"][2]["cutting_zone"] = "PRIMARY_SHEAR_ZONE"
    with pytest.raises(ValidationError, match="COOLANT_ZONE_REQUIREMENTS_INCONSISTENT"):
        CoolantPressureFlowAuditPayload.model_validate(body)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("minimum_required_flow_l_per_min", 1.0, "COOLANT_MINIMUM_FLOW_INCONSISTENT"),
        ("minimum_required_pressure_bar", 1.0, "COOLANT_MINIMUM_PRESSURE_INCONSISTENT"),
        ("flow_margin_percent", 999.0, "COOLANT_FLOW_MARGIN_INCONSISTENT"),
        ("pressure_margin_percent", 999.0, "COOLANT_PRESSURE_MARGIN_INCONSISTENT"),
        (
            "thermal_dissipation_status",
            "INSUFFICIENT_THERMAL_DISSIPATION_WARNING",
            "COOLANT_THERMAL_DISSIPATION_STATUS_INCONSISTENT",
        ),
    ],
)
def test_replayed_contract_rejects_tampered_derived_values(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _payload().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        CoolantPressureFlowAuditPayload.model_validate(body)


def test_invalid_numeric_values_and_authority_promotion_fail_closed() -> None:
    body = _payload().model_dump()
    body["programmed_flow_l_per_min"] = 0.0
    with pytest.raises(ValidationError):
        CoolantPressureFlowAuditPayload.model_validate(body)

    body = _payload().model_dump()
    body["programmed_pressure_bar"] = float("nan")
    with pytest.raises(ValidationError):
        CoolantPressureFlowAuditPayload.model_validate(body)

    body = _payload().model_dump()
    body["automatic_coolant_control_authorized"] = True
    with pytest.raises(ValidationError):
        CoolantPressureFlowAuditPayload.model_validate(body)

    body = _payload().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        CoolantPressureFlowAuditPayload.model_validate(body)
