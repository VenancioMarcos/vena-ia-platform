from __future__ import annotations

from dataclasses import dataclass
from math import fsum, hypot

from app.modules.cnc.schemas import (
    CycleTimeEstimatePayload,
    CycleTimeToolBreakdown,
    ToolpathSegment2D,
)


class CycleTimeEstimatorError(ValueError):
    """Stable failure for a non-deterministic theoretical cycle estimate."""


@dataclass(slots=True)
class _ToolTotals:
    cutting_seconds: float = 0.0
    rapid_seconds: float = 0.0
    cutting_distance: float = 0.0
    rapid_distance: float = 0.0


def _distance(segment: ToolpathSegment2D) -> float:
    return hypot(
        segment.x_end_mm - segment.x_start_mm,
        segment.z_end_mm - segment.z_start_mm,
    )


def estimate_cycle_time(
    segments: tuple[ToolpathSegment2D, ...] | list[ToolpathSegment2D],
    *,
    rapid_feed_rate_mm_min: float = 10_000.0,
) -> CycleTimeEstimatePayload:
    """Estimate theoretical path duration without controlling any machine."""
    if rapid_feed_rate_mm_min <= 0:
        raise CycleTimeEstimatorError("INVALID_RAPID_FEED_RATE")
    if not segments:
        raise CycleTimeEstimatorError("INSUFFICIENT_TOOLPATH_SEGMENTS")

    totals: dict[str, _ToolTotals] = {}
    for segment in segments:
        distance = _distance(segment)
        if distance == 0:
            continue
        tool = segment.active_tool or "UNSPECIFIED_TOOL"
        total = totals.setdefault(tool, _ToolTotals())
        if segment.motion_type == "RAPID":
            total.rapid_distance += distance
            total.rapid_seconds += distance / rapid_feed_rate_mm_min * 60.0
            continue
        feed = segment.effective_feed_mm_min
        if feed is None or feed <= 0:
            raise CycleTimeEstimatorError("INVALID_OR_UNRESOLVED_LINEAR_FEED")
        total.cutting_distance += distance
        total.cutting_seconds += distance / feed * 60.0

    breakdown = tuple(
        CycleTimeToolBreakdown(
            tool=tool,
            cutting_time_seconds=round(total.cutting_seconds, 9),
            rapid_time_seconds=round(total.rapid_seconds, 9),
            cutting_distance_mm=round(total.cutting_distance, 9),
            rapid_distance_mm=round(total.rapid_distance, 9),
        )
        for tool, total in sorted(totals.items())
    )
    return CycleTimeEstimatePayload(
        total_cutting_time_seconds=round(fsum(item.cutting_time_seconds for item in breakdown), 9),
        total_rapid_time_seconds=round(fsum(item.rapid_time_seconds for item in breakdown), 9),
        total_cycle_time_seconds=round(fsum(item.cutting_time_seconds + item.rapid_time_seconds for item in breakdown), 9),
        total_cutting_distance_mm=round(fsum(item.cutting_distance_mm for item in breakdown), 9),
        total_rapid_distance_mm=round(fsum(item.rapid_distance_mm for item in breakdown), 9),
        rapid_feed_rate_mm_min=rapid_feed_rate_mm_min,
        per_tool_breakdown=breakdown,
    )
