from __future__ import annotations

import hashlib
import json
import math
import re

from app.modules.engineering.postprocessor_schemas import (
    GCodeCandidate,
    GCodeCandidateRequest,
    GCodeVerificationEvidence,
)


POSTPROCESSOR_VERSION = "VENA_SYNTHETIC_3AXIS_POST_V1"
MACHINE_PROFILE = "VENA_SYNTHETIC_3AXIS_MILL_V1"
CONTROLLER_PROFILE = "VENA_RS274_SAFE_SUBSET_V1"
_LINE = re.compile(r"^(G(?:0|1|17|21|90|94)|M30)(?: [XYZF]-?\d+(?:\.\d+)?)?(?: [XYZF]-?\d+(?:\.\d+)?)*$")


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class PostprocessorError(Exception):
    pass


class RS274SafeSubsetVerifier:
    """Independent lexical/modal verifier for the minimal synthetic safe subset."""

    def verify(self, program: str, source_hash: str) -> GCodeVerificationEvidence:
        reasons: list[str] = []
        lines = [line.strip() for line in program.splitlines() if line.strip()]
        required_prefix = ["G21", "G17", "G90", "G94"]
        if lines[:4] != required_prefix:
            reasons.append("Metric XY-plane absolute feed/min modal preamble is required.")
        if not lines or lines[-1] != "M30":
            reasons.append("Safe program termination M30 is required.")
        previous: dict[str, float] = {}
        for line in lines:
            if not _LINE.fullmatch(line):
                reasons.append(f"Unsupported RS274 construct: {line}")
                continue
            words = dict(re.findall(r"([XYZF])(-?\d+(?:\.\d+)?)", line))
            for axis, raw in words.items():
                value = float(raw)
                if not math.isfinite(value):
                    reasons.append(f"Non-finite {axis} value.")
                if axis == "F" and value <= 0:
                    reasons.append("Feed must be positive.")
                previous[axis] = value
            if line.startswith("G1 ") and "F" not in words and "F" not in previous:
                reasons.append("Feed motion has no feed mode/value.")
        return GCodeVerificationEvidence(
            status="REJECTED" if reasons else "PASS_REQUIRES_HUMAN_REVIEW",
            checks=["lexical-safe-subset", "modal-preamble", "absolute-metric-xy-feed", "feed-semantics", "safe-termination", "forbidden-code-rejection"],
            rejected_reasons=sorted(set(reasons)),
            replay_hash=_hash({"program": program, "toolpath": source_hash, "verifier": "1.0.0"}),
        )


class SyntheticPostprocessor:
    """Pure, allowlisted synthetic postprocessor; never targets a real controller."""

    def generate(self, request: GCodeCandidateRequest) -> GCodeCandidate:
        path = request.toolpath
        if path.schema_version != "vena-ia.toolpath-candidate/v1":
            raise PostprocessorError("Unsupported toolpath schema.")
        if path.status != "CANDIDATE_FOR_VALIDATION" or path.verification.status != "PASS_REQUIRES_HUMAN_REVIEW":
            raise PostprocessorError("Independently verified toolpath candidate is required.")
        path_hash = _hash(path.model_dump(mode="json"))
        lines = ["G21", "G17", "G90", "G94"]
        for segment in path.segments:
            code = "G0" if segment.motion == "RAPID_CANDIDATE" else "G1"
            words = [f"X{segment.end[0]:.6f}", f"Y{segment.end[1]:.6f}", f"Z{segment.end[2]:.6f}"]
            if code == "G1":
                assert segment.feed_mm_min is not None
                words.append(f"F{segment.feed_mm_min:.6f}")
            lines.append(f"{code} {' '.join(words)}")
        lines.append("M30")
        program = "\n".join(lines)
        output_hash = hashlib.sha256(program.encode()).hexdigest()
        verification = RS274SafeSubsetVerifier().verify(program, path_hash)
        if verification.status == "REJECTED":
            raise PostprocessorError("Generated program did not pass independent verification.")
        manifest = {
            "toolpath_hash": path_hash,
            "manufacturing_model_hash": path.source_manufacturing_model_hash,
            "process_plan_hash": path.source_process_plan_hash,
            "postprocessor_version": POSTPROCESSOR_VERSION,
            "machine_profile": MACHINE_PROFILE,
            "controller_profile": CONTROLLER_PROFILE,
            "output_hash": output_hash,
        }
        return GCodeCandidate(
            source_toolpath_hash=path_hash,
            program=program,
            output_hash=output_hash,
            manifest=manifest,
            verification=verification,
        )
