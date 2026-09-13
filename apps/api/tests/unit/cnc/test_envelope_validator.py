from __future__ import annotations

import pytest

from app.modules.cnc.schemas import MachineEnvelope2D
from app.modules.cnc.services.envelope_validator import (
    KinematicBoundaryViolation,
    validate_kinematic_envelope,
)


def _envelope() -> MachineEnvelope2D:
    return MachineEnvelope2D(
        x_min_mm=0.0,
        x_max_mm=100.0,
        z_min_mm=-100.0,
        z_max_mm=100.0,
        chuck_exclusion_zone={
            "x_min_mm": 25.0,
            "x_max_mm": 35.0,
            "z_min_mm": -10.0,
            "z_max_mm": 0.0,
        },
    )


def test_accepts_safe_rapid_and_linear_trajectories_inside_machine_travel() -> None:
    program = "G00 X80 Z20\nG01 X70 Z10 F0.2\nG1 X60 Z-20 F0.2"

    assert validate_kinematic_envelope(program, _envelope()) == 3


def test_rejects_segment_crossing_chuck_exclusion_zone() -> None:
    program = "G00 X40 Z10\nG01 X20 Z-20 F0.2"

    with pytest.raises(KinematicBoundaryViolation, match="CHUCK_EXCLUSION_ZONE_VIOLATION"):
        validate_kinematic_envelope(program, _envelope())


@pytest.mark.parametrize(
    ("program", "error"),
    (
        ("G00 X101 Z20", "X_AXIS_TRAVEL_LIMIT_EXCEEDED"),
        ("G00 X80 Z-101", "Z_AXIS_TRAVEL_LIMIT_EXCEEDED"),
    ),
)
def test_rejects_axis_travel_overflow(program: str, error: str) -> None:
    with pytest.raises(KinematicBoundaryViolation, match=error):
        validate_kinematic_envelope(program, _envelope())


def test_rejects_incomplete_first_motion_fail_closed() -> None:
    with pytest.raises(
        KinematicBoundaryViolation,
        match="INCOMPLETE_INITIAL_MOTION_COORDINATES",
    ):
        validate_kinematic_envelope("G00 X80", _envelope())
