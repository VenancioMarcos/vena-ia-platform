import pytest
from pydantic import ValidationError

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import MachiningPass, RzPoint, TurningStrategyPlanResponse
from app.modules.cnc.schemas import (
    ChuckProximityAudit,
    CycleTimeEstimatePayload,
    CycleTimeToolBreakdown,
    MachineEnvelope2D,
    MachiningProcessSheetPayload,
    TurningStock2D,
)
from app.modules.cnc.services.process_sheet_generator import (
    PROCESS_SHEET_NOTE,
    ProcessSheetGenerationError,
    generate_process_sheet,
)


def _plan(*, sequences: tuple[int, ...] = (1, 2)) -> TurningStrategyPlanResponse:
    passes = tuple(
        MachiningPass(
            sequence=sequence,
            operation_type=TurningOperationType.ROUGH_TURNING,
            coordinates_rz_mm=(
                RzPoint(r_mm=25 - index, z_mm=0),
                RzPoint(r_mm=24 - index, z_mm=-20),
            ),
            estimated_removed_volume_mm3=1_000 * (index + 1),
        )
        for index, sequence in enumerate(sequences)
    )
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.ROUGH_TURNING,
        passes=passes,
        material_removal_volume_mm3=sum(item.estimated_removed_volume_mm3 for item in passes),
        warnings=("ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW",),
    )


def _cycle() -> CycleTimeEstimatePayload:
    return CycleTimeEstimatePayload(
        total_cutting_time_seconds=120,
        total_rapid_time_seconds=30,
        total_cycle_time_seconds=150,
        total_cutting_distance_mm=100,
        total_rapid_distance_mm=50,
        rapid_feed_rate_mm_min=10_000,
        per_tool_breakdown=(
            CycleTimeToolBreakdown(
                tool="T0101",
                cutting_time_seconds=120,
                rapid_time_seconds=30,
                cutting_distance_mm=100,
                rapid_distance_mm=50,
            ),
        ),
    )


def _sheet(**updates: object) -> MachiningProcessSheetPayload:
    values: dict[str, object] = {
        "part_id": "CAD-PART-001",
        "revision": "A",
        "source_plan_id": "plan-001",
        "cam_plan": _plan(),
        "stock": TurningStock2D(diameter_mm=52, z_min_mm=-100, z_max_mm=2),
        "machine_envelope": MachineEnvelope2D(
            x_min_mm=0,
            x_max_mm=100,
            z_min_mm=-200,
            z_max_mm=200,
            chuck_exclusion_zone={
                "x_min_mm": 0,
                "x_max_mm": 100,
                "z_min_mm": 50,
                "z_max_mm": 100,
            },
        ),
        "chuck_proximity": ChuckProximityAudit(
            minimum_clearance_mm=12,
            threshold_mm=5,
            closest_segment_index=0,
        ),
        "cycle_time_estimate": _cycle(),
        "tool_id": "T0101",
        "tool_description": "ROUGHING TOOL",
        "insert_nose_radius_mm": 0.8,
        "tool_orientation": "RIGHT_HAND",
        "cutting_speed_vc_m_per_min": 180,
        "feed_mm_per_rev": 0.2,
        "depth_of_cut_ap_mm": 2,
        "spindle_rpm": 1_500,
    }
    values.update(updates)
    return generate_process_sheet(**values)  # type: ignore[arg-type]


def test_generates_ordered_setup_and_cam_operations_with_bound_snapshots() -> None:
    sheet = _sheet()
    assert [item.sequence for item in sheet.sequence_operations] == [1, 2, 3]
    assert [item.phase for item in sheet.sequence_operations] == [
        "SETUP",
        "ROUGH_TURNING",
        "ROUGH_TURNING",
    ]
    assert sheet.sequence_operations[1].tool_id == "T0101"
    assert sheet.sequence_operations[1].insert_reference == "INSERT_R0.800_RIGHT_HAND"
    assert sheet.sequence_operations[1].feed_rate_mm_min == pytest.approx(300)
    assert sum(item.estimated_time_min for item in sheet.sequence_operations[1:]) == pytest.approx(2.5)
    assert sheet.estimated_total_time_min == pytest.approx(17.5)
    assert sheet.total_operations_count == 3
    assert sheet.is_theoretical_sheet is True
    assert sheet.physical_use_authorized is False
    assert PROCESS_SHEET_NOTE.startswith("FOLHA DE PROCESSO TEÓRICA ANALÍTICA")


@pytest.mark.parametrize(
    ("updates", "error"),
    [
        ({"cam_plan": _plan(sequences=(2, 1))}, "PROCESS_SHEET_CAM_SEQUENCE_INVALID"),
        ({"setup_time_min": -1}, "PROCESS_SHEET_PARAMETERS_INVALID"),
        (
            {"stock": TurningStock2D(diameter_mm=120, z_min_mm=-100, z_max_mm=2)},
            "PROCESS_SHEET_CLAMPING_INVALID",
        ),
        (
            {
                "chuck_proximity": ChuckProximityAudit(
                    minimum_clearance_mm=0,
                    threshold_mm=5,
                    closest_segment_index=0,
                    warning_code="WARNING_PROXIMITY_CHUCK",
                )
            },
            "PROCESS_SHEET_CLAMPING_INVALID",
        ),
    ],
)
def test_rejects_unordered_cam_invalid_time_or_clamping(updates, error) -> None:
    with pytest.raises(ProcessSheetGenerationError, match=error):
        _sheet(**updates)


@pytest.mark.parametrize(
    ("mutate", "error"),
    [
        (
            lambda body: body["sequence_operations"][1].update(feed_rate_mm_min=301),
            "PROCESS_SHEET_FEED_RATE_INCONSISTENT",
        ),
        (
            lambda body: body["sequence_operations"][1].update(estimated_time_min=20),
            "PROCESS_SHEET_TIME_SOURCE_INCONSISTENT",
        ),
        (
            lambda body: body["raw_stock_dimensions"].update(diameter_mm=51),
            "PROCESS_SHEET_STOCK_SOURCE_INCONSISTENT",
        ),
    ],
)
def test_contract_rejects_forged_operation_and_source_snapshots(mutate, error) -> None:
    body = _sheet().model_dump()
    mutate(body)
    with pytest.raises(ValidationError, match=error):
        MachiningProcessSheetPayload.model_validate(body)
