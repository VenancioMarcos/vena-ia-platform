from __future__ import annotations

import hashlib
import json
from typing import Literal

from app.modules.engineering.blind_validation_schemas import (
    ControlledBlindValidationEvidence,
    ControlledBlindValidationRequest,
    GateEvidence,
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class ControlledBlindValidationService:
    """Freezes artifacts before later comparison; never reads a sealed reference body."""

    def freeze(self, request: ControlledBlindValidationRequest) -> ControlledBlindValidationEvidence:
        model = request.manufacturing_model
        path = request.toolpath
        gcode = request.gcode_candidate
        level2 = request.level2_evidence
        artifacts = {
            "cad": request.cad_hash,
            "topology": model.final_geometry.topology_evidence_hash,
            "manufacturing_model": _hash(model.model_dump(mode="json")),
            "process_plan": model.verification.deterministic_replay_hash,
            "toolpath": _hash(path.model_dump(mode="json")),
            "gcode_candidate": gcode.output_hash,
            "level2_evidence": _hash(level2.model_dump(mode="json")),
        }
        resource_pass = bool(
            model.recommendation
            and not model.recommendation.compatibility.endswith("INCOMPATIBLE")
        )
        gate_values: list[
            tuple[
                Literal["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"],
                bool,
                str,
            ]
        ] = [
            ("G0", bool(request.cad_hash), "cad"),
            ("G1", model.final_geometry.topology_valid, "topology"),
            ("G2", model.status == "READY_FOR_REVIEW", "manufacturing_model"),
            ("G3", model.verification.status == "PASS_REQUIRES_HUMAN_REVIEW", "process_plan"),
            ("G4", resource_pass, "manufacturing_model"),
            ("G5", path.verification.status == "PASS_REQUIRES_HUMAN_REVIEW", "toolpath"),
            ("G6", gcode.postprocessor_version == "VENA_SYNTHETIC_3AXIS_POST_V1", "gcode_candidate"),
            ("G7", gcode.verification.status == "PASS_REQUIRES_HUMAN_REVIEW", "gcode_candidate"),
            ("G8", level2.status == "PASS_REQUIRES_HUMAN_REVIEW", "level2_evidence"),
        ]
        gates = [
            GateEvidence(gate=gate, status="PASS" if passed else "FAIL", evidence_ref=artifacts[ref])
            for gate, passed, ref in gate_values
        ]
        gates.append(
            GateEvidence(
                gate="G9",
                status="PENDING_REVIEW",
                evidence_ref="PENDING_AUTHORITATIVE_SERVER_SIDE_HUMAN_REVIEW",
            )
        )
        bundle_hash = _hash(
            {
                "holdout": request.holdout_id,
                "sealed": request.sealed_reference_hash,
                "artifacts": artifacts,
            }
        )
        ready = all(gate.status == "PASS" for gate in gates)
        return ControlledBlindValidationEvidence(
            holdout_id=request.holdout_id,
            sealed_reference_hash=request.sealed_reference_hash,
            frozen_artifact_hashes=artifacts,
            frozen_bundle_hash=bundle_hash,
            gates=gates,
            questions_asked=request.questions_asked,
            omissions=[],
            false_positives=[],
            process_divergence="PENDING_SEALED_REFERENCE_ADJUDICATION",
            toolpath_divergence="PENDING_SEALED_REFERENCE_ADJUDICATION",
            human_adjudication="PENDING_AUTHORITATIVE_REVIEW",
            replay_hash=_hash(
                {
                    "bundle": bundle_hash,
                    "gates": [gate.model_dump(mode="json") for gate in gates],
                }
            ),
            cad_to_gcode_controlled_validation_ready=ready,
            limitations=[
                "The sealed reference body is never loaded by this harness.",
                "Omissions, false positives and divergence require later human adjudication.",
                "G9 authority cannot originate from the public request payload.",
                "No artifact grants physical or production authority.",
            ],
        )
