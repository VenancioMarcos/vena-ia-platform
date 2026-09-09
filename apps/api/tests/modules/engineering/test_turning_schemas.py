from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.modules.engineering.turning_schemas import (
    ControllerProfileRequirement,
    TurningProfile2D,
    TurningProfilePoint,
    TurningStockCylinder,
    TurningToolDefinition,
)


@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf"), "2.0", True])
def test_radius_rejects_invalid_or_coerced_values(value: object) -> None:
    with pytest.raises(ValidationError):
        TurningProfilePoint.model_validate({"radius_mm": value, "z_mm": 0.0})


@pytest.mark.parametrize("field,value", [
    ("diameter_mm", 0.0), ("diameter_mm", -1.0), ("length_mm", 0.0),
    ("length_mm", float("inf")), ("face_allowance_mm", -1.0),
    ("face_allowance_mm", 20.0), ("face_allowance_mm", float("nan")),
])
def test_stock_requires_usable_finite_dimensions(field: str, value: float) -> None:
    data = {"diameter_mm": 10.0, "length_mm": 20.0, "face_allowance_mm": 0.0}
    data[field] = value
    with pytest.raises(ValidationError):
        TurningStockCylinder.model_validate(data)


def test_json_profile_roundtrip_preserves_radial_coordinates() -> None:
    payload = {
        "points": [{"radius_mm": 0.0, "z_mm": 0.0}, {"radius_mm": 5.0, "z_mm": -20.0}],
        "axis_origin": [10.0, 20.0, 30.0], "axis_direction": [0.0, 0.0, -1.0],
        "is_closed": False,
    }
    profile = TurningProfile2D.model_validate_json(json.dumps(payload))
    assert profile.points[1].radius_mm == 5.0  # No premature diameter conversion.
    assert profile.axis_direction == (0.0, 0.0, -1.0)
    assert TurningProfile2D.model_validate_json(profile.model_dump_json()) == profile
    with pytest.raises(ValidationError):
        profile.points[1].radius_mm = -1.0


@pytest.mark.parametrize("update", [
    {"axis_direction": [0.0, 0.0, 0.0]}, {"axis_direction": [0.0, 0.0, 2.0]},
    {"axis_origin": [0.0, 0.0, float("nan")]}, {"is_closed": True},
    {"is_closed": "false"}, {"physical_use_authorized": True}, {"points": []},
    {"points": [{"radius_mm": 1.0, "z_mm": 0.0}] * 2},
])
def test_profile_rejects_inconsistent_declarations(update: dict[str, object]) -> None:
    payload = {
        "points": [{"radius_mm": 0.0, "z_mm": 0.0}, {"radius_mm": 5.0, "z_mm": -20.0}],
        "axis_origin": [0.0, 0.0, 0.0], "axis_direction": [0.0, 0.0, 1.0],
        "is_closed": False,
    }
    payload.update(update)
    with pytest.raises(ValidationError):
        TurningProfile2D.model_validate_json(json.dumps(payload))


def test_explicit_closed_profile_and_zero_face_allowance() -> None:
    points = tuple(TurningProfilePoint(radius_mm=r, z_mm=z)
                   for r, z in [(0.0, 0.0), (5.0, 0.0), (5.0, -10.0), (0.0, 0.0)])
    profile = TurningProfile2D(points=points, axis_origin=(0.0, 0.0, 0.0),
                              axis_direction=(0.0, 0.0, 1.0), is_closed=True)
    assert profile.is_closed
    assert TurningStockCylinder(diameter_mm=10.0, length_mm=20.0,
                                face_allowance_mm=0.0).face_allowance_mm == 0.0


@pytest.mark.parametrize("update", [
    {"tool_id": "  "}, {"insert_radius_mm": 0.0}, {"hand": "UNKNOWN"},
    {"clearance_angle_deg": -1.0}, {"clearance_angle_deg": 90.0},
    {"clearance_angle_deg": float("nan")}, {"insert_radius_mm": "0.8"},
])
def test_tool_requires_explicit_bounded_data(update: dict[str, object]) -> None:
    payload = {"tool_id": "external", "insert_radius_mm": 0.8,
               "hand": "RIGHT", "clearance_angle_deg": 0.0}
    payload.update(update)
    with pytest.raises(ValidationError):
        TurningToolDefinition.model_validate(payload)


@pytest.mark.parametrize("mode", ["RADIUS", "DIAMETER"])
def test_controller_declaration_never_resolves_emission(mode: str) -> None:
    requirement = ControllerProfileRequirement.model_validate({
        "controller_id": "unverified-example", "x_mode": mode,
        "feed_mode": "MM_PER_REVOLUTION",
    })
    assert requirement.emission_status == "CONTROLLER_PROFILE_UNRESOLVED"
    with pytest.raises(ValidationError):
        ControllerProfileRequirement.model_validate({
            **requirement.model_dump(), "emission_status": "APPROVED",
        })
    with pytest.raises(ValidationError):
        ControllerProfileRequirement.model_validate({
            **requirement.model_dump(), "feed_mode": "G95",
        })
