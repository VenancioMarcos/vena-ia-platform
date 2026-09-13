from __future__ import annotations

import pytest

from app.modules.cnc.enums import CNCControllerType
from app.modules.cnc.schemas import MachineEnvelope2D, TurningStock2D
from app.modules.cnc.services.simulation_parser import parse_toolpath_simulation


def _envelope() -> MachineEnvelope2D:
    return MachineEnvelope2D(
        x_min_mm=0.0,
        x_max_mm=100.0,
        z_min_mm=-200.0,
        z_max_mm=200.0,
        chuck_exclusion_zone={
            "x_min_mm": 0.0,
            "x_max_mm": 100.0,
            "z_min_mm": 50.0,
            "z_max_mm": 100.0,
        },
    )


def _stock() -> TurningStock2D:
    return TurningStock2D(diameter_mm=52.0, z_min_mm=-100.0, z_max_mm=1.0)


@pytest.mark.parametrize(
    ("controller", "preamble", "rapid", "linear", "expected_tool"),
    (
        (CNCControllerType.FANUC_0I, "T0101", "G00", "G01", "T0101"),
        (
            CNCControllerType.SIEMENS_840D,
            'T="FINISH TOOL" D1',
            "G0",
            "G1",
            "FINISH TOOL/D1",
        ),
        (CNCControllerType.HAAS, "T0202", "G00", "G01", "T0202"),
    ),
)
def test_decomposes_supported_dialects_into_deterministic_2d_segments(
    controller: CNCControllerType,
    preamble: str,
    rapid: str,
    linear: str,
    expected_tool: str,
) -> None:
    program = "\n".join(
        (
            preamble,
            f"{rapid} X50 Z5",
            f"{rapid} X40 Z2",
            f"{linear} X36 Z2 F0.2",
            f"{linear} Z-20",
            "M05",
            "M30",
        )
    )

    first = parse_toolpath_simulation(
        program,
        controller_profile=controller,
        machine_envelope=_envelope(),
        stock=_stock(),
        source_plan_id="plan-sim-001",
    )
    second = parse_toolpath_simulation(
        program,
        controller_profile=controller,
        machine_envelope=_envelope(),
        stock=_stock(),
        source_plan_id="plan-sim-001",
    )

    assert first == second
    assert len(first.segments) == 3
    assert first.segments[0].model_dump() == {
        "motion_type": "RAPID",
        "x_start_mm": 50.0,
        "z_start_mm": 5.0,
        "x_end_mm": 40.0,
        "z_end_mm": 2.0,
        "feed": None,
        "active_tool": expected_tool,
    }
    assert first.segments[1].motion_type == "LINEAR"
    assert first.segments[1].feed == 0.2
    assert first.segments[2].x_start_mm == 36.0
    assert first.segments[2].z_end_mm == -20.0


def test_payload_preserves_visualization_metadata_and_safety_invariants() -> None:
    result = parse_toolpath_simulation(
        "G00 X40 Z2\nG01 X36 Z-20 F0.15",
        controller_profile=CNCControllerType.FANUC_0I,
        machine_envelope=_envelope(),
        stock=_stock(),
    )

    assert result.status == "SIMULATION_READY_REQUIRES_REVIEW"
    assert result.coordinate_convention == "LATHE_X_DIAMETER_Z"
    assert result.machine_envelope == _envelope()
    assert result.stock == _stock()
    assert result.safety_flags.physical_use_authorized is False
    assert result.safety_flags.machine_send is False
    assert result.safety_flags.executable_output is False
