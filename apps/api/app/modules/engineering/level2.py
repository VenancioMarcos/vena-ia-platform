from __future__ import annotations

import hashlib
import json
import math
from typing import Literal

from app.modules.engineering.level2_schemas import Level2VerificationEvidence, Level2VerificationRequest


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _inside(
    point: tuple[float, float, float],
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
    margin: float = 0.0,
) -> bool:
    return all(bounds[0][i] - margin <= point[i] <= bounds[1][i] + margin for i in range(3))


class Level2Verifier:
    """Independent endpoint/sweep approximation; not a machine-kinematics simulator."""

    def verify(self, request: Level2VerificationRequest) -> Level2VerificationEvidence:
        model, path = request.manufacturing_model, request.toolpath
        reasons: list[str] = []
        missing_inputs = False
        if (
            path.status != "CANDIDATE_FOR_VALIDATION"
            or path.verification.status != "PASS_REQUIRES_HUMAN_REVIEW"
        ):
            reasons.append("Verified toolpath candidate is required.")
        if model.stock.minimum is None or model.stock.maximum is None:
            reasons.append("Explicit stock bounds are required for Level-2 evidence.")
            missing_inputs = True
        elif model.stock.contains_final_geometry is not True:
            reasons.append("Stock evidence is invalid or insufficient for the final geometry.")
        stock = (
            (model.stock.minimum, model.stock.maximum)
            if model.stock.minimum and model.stock.maximum
            else None
        )
        protected = model.final_geometry.bounds
        radius = path.tool.diameter_mm / 2
        previous = None
        covered: set[str] = set()
        sweep = 0.0
        gouge = rapid = fixture = False
        if not path.segments:
            reasons.append("A non-empty reconstructed trajectory is required.")
        for segment in path.segments:
            if not all(
                math.isfinite(value)
                for point in (segment.start, segment.end)
                for value in point
            ):
                reasons.append(f"Segment {segment.segment_id} has non-finite coordinates.")
                continue
            if previous is not None and segment.start != previous:
                reasons.append(f"Reconstruction discontinuity at {segment.segment_id}.")
            previous = segment.end
            length = math.dist(segment.start, segment.end)
            if segment.motion == "FEED_CANDIDATE":
                sweep += math.pi * radius * radius * length
                if segment.target_region_id:
                    covered.add(segment.target_region_id)
                if _inside(segment.start, protected, radius) or _inside(segment.end, protected, radius):
                    gouge = True
            if segment.motion == "RAPID_CANDIDATE" and (
                _inside(segment.start, protected, radius)
                or _inside(segment.end, protected, radius)
            ):
                rapid = True
            for keep_out in request.fixture_keep_outs:
                bounds = (keep_out.minimum, keep_out.maximum)
                if _inside(segment.start, bounds, radius) or _inside(segment.end, bounds, radius):
                    fixture = True
            if (
                stock
                and segment.motion == "FEED_CANDIDATE"
                and not (_inside(segment.start, stock) or _inside(segment.end, stock))
            ):
                reasons.append(f"Feed segment {segment.segment_id} never intersects stock envelope.")
        expected = {region.region_id for region in model.removal_regions}
        if gouge:
            reasons.append("Simplified cutter sweep intersects protected final envelope.")
        if rapid:
            reasons.append("Rapid candidate intersects protected final envelope.")
        if fixture:
            reasons.append("Candidate intersects supplied fixture/keep-out evidence.")
        coverage = "COMPLETE" if expected and expected <= covered else "INCOMPLETE"
        if coverage != "COMPLETE":
            reasons.append("Target coverage is incomplete.")
        status: Literal[
            "REJECTED", "PASS_REQUIRES_HUMAN_REVIEW", "REQUIRES_INPUT"
        ] = (
            "REQUIRES_INPUT"
            if missing_inputs
            else "REJECTED"
            if reasons
            else "PASS_REQUIRES_HUMAN_REVIEW"
        )
        return Level2VerificationEvidence(
            status=status,
            replay_hash=_hash(
                {
                    "model": model.model_dump(mode="json"),
                    "path": path.model_dump(mode="json"),
                    "keep_outs": [item.model_dump(mode="json") for item in request.fixture_keep_outs],
                }
            ),
            reconstructed_segment_count=len(path.segments),
            simplified_sweep_volume_mm3=round(sweep, 6),
            target_coverage=coverage,
            remaining_material="NOT_CALCULATED_EXACT_BREP",
            gouge_detected=gouge,
            protected_surface_violation=gouge,
            rapid_collision_detected=rapid,
            fixture_collision_detected=fixture if request.fixture_keep_outs else None,
            geometric_error="NOT_CALCULATED_EXACT_BREP",
            checks=[
                "independent-reconstruction",
                "endpoint-cylinder-sweep",
                "stock-envelope",
                "protected-envelope",
                "rapid",
                "fixture-keep-out",
                "target-coverage",
                "replay",
            ],
            rejected_reasons=sorted(set(reasons)),
            limitations=[
                "Level 2 uses endpoint/cylindrical sweep approximation only; no exact B-Rep subtraction, holder collision or machine kinematics.",
                "Physical validation remains false.",
            ],
        )
