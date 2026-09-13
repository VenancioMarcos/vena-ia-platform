from __future__ import annotations

import pytest

from app.modules.cnc.schemas import ToolpathSegment2D
from app.modules.cnc.services.cycle_time_estimator import CycleTimeEstimatorError, estimate_cycle_time


def test_estimates_linear_and_rapid_distances_and_times_deterministically() -> None:
    estimate = estimate_cycle_time((
        ToolpathSegment2D(motion_type="RAPID", x_start_mm=0, z_start_mm=0, x_end_mm=3, z_end_mm=4, active_tool="T01"),
        ToolpathSegment2D(motion_type="LINEAR", x_start_mm=3, z_start_mm=4, x_end_mm=3, z_end_mm=14, feed=120, effective_feed_mm_min=120, active_tool="T01"),
    ), rapid_feed_rate_mm_min=600)
    assert estimate.total_rapid_distance_mm == 5
    assert estimate.total_cutting_distance_mm == 10
    assert estimate.total_rapid_time_seconds == 0.5
    assert estimate.total_cutting_time_seconds == 5
    assert estimate.total_cycle_time_seconds == 5.5


def test_groups_metrics_by_active_tool_and_ignores_zero_length_blocks() -> None:
    estimate = estimate_cycle_time((
        ToolpathSegment2D(motion_type="LINEAR", x_start_mm=0, z_start_mm=0, x_end_mm=1, z_end_mm=0, feed=60, effective_feed_mm_min=60, active_tool="T01"),
        ToolpathSegment2D(motion_type="RAPID", x_start_mm=1, z_start_mm=0, x_end_mm=1, z_end_mm=0, active_tool="T02"),
        ToolpathSegment2D(motion_type="LINEAR", x_start_mm=1, z_start_mm=0, x_end_mm=1, z_end_mm=2, feed=60, effective_feed_mm_min=60, active_tool="T02"),
    ))
    assert [(item.tool, item.cutting_distance_mm) for item in estimate.per_tool_breakdown] == [("T01", 1), ("T02", 2)]


def test_rejects_unresolved_linear_feed_fail_closed() -> None:
    segment = ToolpathSegment2D(motion_type="LINEAR", x_start_mm=0, z_start_mm=0, x_end_mm=1, z_end_mm=0, feed=0.1, active_tool="T01")
    with pytest.raises(CycleTimeEstimatorError, match="INVALID_OR_UNRESOLVED_LINEAR_FEED"):
        estimate_cycle_time((segment,))
