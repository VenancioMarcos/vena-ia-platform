from __future__ import annotations

import hashlib
import json
import math
from typing import Literal, cast

from app.modules.engineering.manufacturing_schemas import ManufacturingGeometryModel
from app.modules.engineering.toolpath_schemas import (
    Point3D,
    ToolpathCandidate,
    ToolpathCandidateRequest,
    ToolpathSegment,
    ToolpathVerificationEvidence,
)


TOOLPATH_RULE_VERSION = "1.0.0"


def _hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _inside(point: Point3D, bounds: tuple[Point3D, Point3D], margin: float = 0.0) -> bool:
    return all(
        bounds[0][axis] - margin <= point[axis] <= bounds[1][axis] + margin
        for axis in range(3)
    )


def _midpoint(bounds: tuple[Point3D, Point3D]) -> Point3D:
    return tuple(round((bounds[0][axis] + bounds[1][axis]) / 2, 6) for axis in range(3))  # type: ignore[return-value]


class ToolpathCandidateError(Exception):
    pass


class ToolpathVerifier:
    """Independent structural verifier; it never trusts the candidate generator."""

    def verify(
        self,
        candidate: ToolpathCandidate,
        model: ManufacturingGeometryModel,
    ) -> ToolpathVerificationEvidence:
        rejected: list[str] = []
        checks = [
            "linear-primitive-allowlist",
            "finite-coordinate-check",
            "machine-bounds-check",
            "segment-continuity-check",
            "feed-rapid-semantics-check",
            "protected-envelope-preliminary-avoidance",
            "target-region-reference-check",
            "deterministic-replay-check",
        ]
        machine_bounds = candidate.machine_bounds
        protected = model.final_geometry.bounds
        expected_targets = {region.region_id for region in model.removal_regions}
        referenced_targets = {segment.target_region_id for segment in candidate.segments if segment.target_region_id}
        if not referenced_targets or not referenced_targets <= expected_targets:
            rejected.append("Unknown or missing removal-region target.")
        previous: Point3D | None = None
        tool_radius = candidate.tool.diameter_mm / 2
        for segment in candidate.segments:
            if segment.primitive != "LINEAR":
                rejected.append(f"Unsupported primitive {segment.primitive}.")
            if segment.motion == "FEED_CANDIDATE" and segment.feed_mm_min is None:
                rejected.append(f"Feed segment {segment.segment_id} has no feed.")
            if segment.motion == "RAPID_CANDIDATE" and segment.feed_mm_min is not None:
                rejected.append(f"Rapid segment {segment.segment_id} has a feed.")
            if previous is not None and segment.start != previous:
                rejected.append(f"Segment {segment.segment_id} is discontinuous.")
            previous = segment.end
            for point in (segment.start, segment.end):
                if not all(math.isfinite(value) for value in point):
                    rejected.append(f"Segment {segment.segment_id} has non-finite coordinates.")
                if not _inside(point, machine_bounds):
                    rejected.append(f"Segment {segment.segment_id} exceeds machine bounds.")
                if segment.motion == "FEED_CANDIDATE" and _inside(point, protected, tool_radius):
                    rejected.append(
                        f"Feed segment {segment.segment_id} enters protected final geometry envelope."
                    )
        seed = {
            "rule": TOOLPATH_RULE_VERSION,
            "candidate": candidate.model_dump(mode="json", exclude={"verification"}),
            "model_hash": _hash(model.model_dump(mode="json")),
        }
        return ToolpathVerificationEvidence(
            status="REJECTED" if rejected else "PASS_REQUIRES_HUMAN_REVIEW",
            deterministic_replay_hash=_hash(seed),
            checks=checks,
            rejected_reasons=sorted(set(rejected)),
            limitations=[
                "Verification is structural and preliminary; it is not cutter-sweep, collision or material-removal simulation.",
                "Holder, fixture and keep-out collision evidence is not proven by this Package 1 verifier.",
            ],
        )


class ToolpathCandidateService:
    """Creates bounded, non-executable 3-axis linear toolpath candidates only."""

    def create(self, request: ToolpathCandidateRequest) -> ToolpathCandidate:
        model = request.manufacturing_model
        if model.schema_version != "vena-ia.manufacturing-geometry-model/v1":
            raise ToolpathCandidateError("Unsupported manufacturing model schema.")
        if model.planning_schema_version != "vena-ia.verified-process-plan/v1":
            raise ToolpathCandidateError("Verified process-plan evidence is required.")
        if model.status != "READY_FOR_REVIEW":
            raise ToolpathCandidateError("Manufacturing model is not ready for reviewed toolpath candidacy.")
        operation = next(
            (item for item in model.operation_candidates if item.candidate_id == request.operation_candidate_id),
            None,
        )
        if operation is None or operation.status != "CANDIDATE_REQUIRES_HUMAN_REVIEW":
            raise ToolpathCandidateError("An explicit reviewed operation candidate is required.")
        if request.clearance_z_mm > request.machine_maximum[2]:
            raise ToolpathCandidateError("Clearance exceeds bounded machine envelope.")
        if request.retract_z_mm < request.machine_minimum[2]:
            raise ToolpathCandidateError("Retract exceeds bounded machine envelope.")

        source_hash = _hash(model.model_dump(mode="json"))
        process_hash = model.verification.deterministic_replay_hash
        start: Point3D = (
            request.machine_minimum[0],
            request.machine_minimum[1],
            request.clearance_z_mm,
        )
        current = start
        segments: list[ToolpathSegment] = []
        for region in model.removal_regions:
            if region.region_id not in operation.target_region_refs or region.bounds is None:
                continue
            target = _midpoint(region.bounds)
            safe_target = (target[0], target[1], request.clearance_z_mm)
            approach = (target[0], target[1], target[2])
            for end, motion, feed, region_id in (
                (safe_target, "RAPID_CANDIDATE", None, None),
                (approach, "FEED_CANDIDATE", request.feed_mm_min, region.region_id),
                (safe_target, "FEED_CANDIDATE", request.feed_mm_min, region.region_id),
            ):
                segment_id = f"segment-{_hash([current, end, motion, region_id])[:16]}"
                segments.append(
                    ToolpathSegment(
                        segment_id=segment_id,
                        motion=cast(Literal["RAPID_CANDIDATE", "FEED_CANDIDATE"], motion),
                        start=current,
                        end=end,
                        feed_mm_min=feed,
                        target_region_id=region_id,
                    )
                )
                current = end
        if not segments:
            raise ToolpathCandidateError("No authorized removable regions exist for the operation.")
        segments.append(
            ToolpathSegment(
                segment_id=f"segment-{_hash([current, start, 'return'])[:16]}",
                motion="RAPID_CANDIDATE",
                start=current,
                end=start,
            )
        )
        candidate = ToolpathCandidate(
            status="CANDIDATE_FOR_VALIDATION",
            source_manufacturing_model_hash=source_hash,
            source_process_plan_hash=process_hash,
            operation_candidate_id=operation.candidate_id,
            tool=request.tool,
            machine_bounds=(request.machine_minimum, request.machine_maximum),
            clearance_z_mm=request.clearance_z_mm,
            retract_z_mm=request.retract_z_mm,
            target_region_ids=sorted({segment.target_region_id for segment in segments if segment.target_region_id}),
            segments=segments,
            limitations=[
                "Linear 3-axis/2.5D candidate only; no arcs, freeform CAM, 4/5-axis or turning.",
                "Candidate is non-executable and cannot be sent to any controller or machine.",
            ],
            verification=ToolpathVerificationEvidence(
                status="REJECTED",
                deterministic_replay_hash="PENDING_INDEPENDENT_VERIFICATION",
                checks=[],
                rejected_reasons=[],
                limitations=[],
            ),
        )
        verification = ToolpathVerifier().verify(candidate, model)
        return candidate.model_copy(
            update={
                "status": "REJECTED" if verification.status == "REJECTED" else "CANDIDATE_FOR_VALIDATION",
                "verification": verification,
            }
        )
