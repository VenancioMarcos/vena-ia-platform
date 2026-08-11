from __future__ import annotations

import hashlib
import json

from app.modules.engineering.blind_validation import ControlledBlindValidationService
from app.modules.engineering.blind_validation_schemas import ControlledBlindValidationEvidence
from app.modules.engineering.digital_thread import DigitalThreadService
from app.modules.engineering.digital_thread_schemas import DigitalThreadManifest
from app.modules.engineering.g9_review_schemas import G9ReviewPackage
from app.modules.engineering.level2_schemas import Level2VerificationEvidence
from app.modules.engineering.postprocessor import RS274SafeSubsetVerifier
from app.modules.engineering.postprocessor_schemas import GCodeCandidate


class G9ReviewPackageError(ValueError):
    pass


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class G9ReviewPackageService:
    """Builds reproducible review input while preserving the external G9 boundary."""

    HUMAN_REVIEW_PROTOCOL = (
        "Authenticate the qualified reviewer and revalidate active Organization membership.",
        "Record reviewer qualification and conflict-of-interest declaration.",
        "Recompute this package, Digital Thread, blind bundle and candidate hashes.",
        "Review G0-G8 evidence, limitations, unresolved risks and external evidence.",
        "Record reject/request-correction/next-stage disposition outside this public contract.",
        "Bind any future disposition to exact hashes, versions, timestamp and revocation rules.",
    )
    EXTERNAL_VALIDATION_PROTOCOL = (
        "Use an independent simulator and record vendor, version and configuration hash.",
        "Bind machine/controller, stock, workholding, fixture, datum/WCS, tool/holder and offsets.",
        "Evaluate controller semantics, travel, kinematics, collisions and machine limits.",
        "Evaluate material removal, remaining stock, gouge and protected surfaces.",
        "Export deterministic traces and bind every result to the exact candidate hash.",
        "Return evidence for human adjudication; never mutate G9 automatically.",
    )
    REQUIRED_EXTERNAL_ARTIFACTS = (
        "simulator_identity_and_version",
        "machine_controller_configuration_hash",
        "stock_and_workholding_definition",
        "tool_holder_offset_configuration",
        "datum_wcs_definition",
        "collision_and_kinematic_evidence",
        "material_removal_evidence",
        "controller_semantics_evidence",
        "trace_and_replay_artifacts",
        "exact_candidate_hash_binding",
    )

    def build(
        self,
        candidate: GCodeCandidate,
        level2: Level2VerificationEvidence,
        blind: ControlledBlindValidationEvidence,
        thread: DigitalThreadManifest,
    ) -> G9ReviewPackage:
        payload = self._payload(candidate, level2, blind, thread)
        package_hash = _hash(payload)
        package = G9ReviewPackage.model_validate(
            {
                "package_id": f"g9-package-{package_hash[:24]}",
                "package_hash": package_hash,
                **payload,
            }
        )
        if not self.validate(package, candidate, level2, blind, thread):
            raise G9ReviewPackageError("G9 review package failed deterministic validation.")
        return package

    @classmethod
    def validate(
        cls,
        package: G9ReviewPackage,
        candidate: GCodeCandidate,
        level2: Level2VerificationEvidence,
        blind: ControlledBlindValidationEvidence,
        thread: DigitalThreadManifest,
    ) -> bool:
        try:
            expected = cls()._payload(candidate, level2, blind, thread)
            package_payload = package.model_dump(
                mode="json", exclude={"package_id", "package_hash"}
            )
            expected_hash = _hash(expected)
            return bool(
                package_payload == expected
                and package.package_hash == expected_hash
                and package.package_id == f"g9-package-{expected_hash[:24]}"
            )
        except (KeyError, ValueError):
            return False

    def _payload(
        self,
        candidate: GCodeCandidate,
        level2: Level2VerificationEvidence,
        blind: ControlledBlindValidationEvidence,
        thread: DigitalThreadManifest,
    ) -> dict[str, object]:
        if not DigitalThreadService.validate(thread):
            raise G9ReviewPackageError("Digital Thread replay validation failed.")
        if not ControlledBlindValidationService.validate(blind):
            raise G9ReviewPackageError("Blind validation replay failed.")
        verification = RS274SafeSubsetVerifier().verify(
            candidate.program, candidate.source_toolpath_hash
        )
        if verification != candidate.verification:
            raise G9ReviewPackageError("Level-1 verification replay failed.")
        if hashlib.sha256(candidate.program.encode()).hexdigest() != candidate.output_hash:
            raise G9ReviewPackageError("Candidate output hash mismatch.")
        artifacts = {item.artifact_type: item for item in thread.artifacts}
        candidate_hash = _hash(candidate.model_dump(mode="json"))
        blind_hash = _hash(blind.model_dump(mode="json"))
        level2_hash = _hash(level2.model_dump(mode="json"))
        if artifacts["GCODE_CANDIDATE"].content_hash != candidate_hash:
            raise G9ReviewPackageError("Digital Thread candidate binding mismatch.")
        if artifacts["VERIFICATION_EVIDENCE"].content_hash != level2_hash:
            raise G9ReviewPackageError("Digital Thread Level-2 binding mismatch.")
        if artifacts["REPORT"].content_hash != blind_hash:
            raise G9ReviewPackageError("Digital Thread blind-report binding mismatch.")
        if blind.frozen_artifact_hashes.get("gcode_candidate") != candidate.output_hash:
            raise G9ReviewPackageError("Blind candidate binding mismatch.")
        if blind.frozen_artifact_hashes.get("level2_evidence") != level2_hash:
            raise G9ReviewPackageError("Blind Level-2 binding mismatch.")
        if thread.g9_state != "PENDING_AUTHORITATIVE_REVIEW":
            raise G9ReviewPackageError("G9 must remain pending authoritative review.")
        automatic_gates = tuple(gate for gate in blind.gates if gate.gate != "G9")
        if len(automatic_gates) != 9 or any(gate.status != "PASS" for gate in automatic_gates):
            raise G9ReviewPackageError("G0-G8 evidence is incomplete.")

        return {
            "schema_version": "vena-ia.g9-review-package/v1",
            "organization_id": thread.organization_id,
            "candidate_output_hash": candidate.output_hash,
            "digital_thread_id": thread.thread_id,
            "digital_thread_replay_hash": thread.replay_hash,
            "blind_validation_bundle_hash": blind.frozen_bundle_hash,
            "blind_validation_replay_hash": blind.replay_hash,
            "artifact_hashes": {
                item.artifact_type: item.content_hash for item in thread.artifacts
            },
            "contract_versions": {
                item.artifact_type: item.schema_version for item in thread.artifacts
            }
            | {
                "G9_REVIEW_PACKAGE": "vena-ia.g9-review-package/v1",
                "BLIND_VALIDATION": blind.schema_version,
                "LEVEL1_VERIFICATION": candidate.verification.schema_version,
            },
            "component_versions": {
                "machine_profile": candidate.machine_profile,
                "controller_profile": candidate.controller_profile,
                "postprocessor": candidate.postprocessor_version,
                "level1_verifier": "VENA_RS274_SAFE_SUBSET_VERIFIER_1.0.0",
                "level2_verifier": level2.schema_version,
            },
            "gates": [gate.model_dump(mode="json") for gate in blind.gates],
            "level1_status": candidate.verification.status,
            "level1_replay_hash": candidate.verification.replay_hash,
            "level2_status": level2.status,
            "level2_replay_hash": level2.replay_hash,
            "classification": "CANDIDATE_FOR_VALIDATION",
            "evidence_lifecycle": "CURRENT",
            "g9_state": "PENDING_AUTHORITATIVE_REVIEW",
            "known_limitations": list(
                dict.fromkeys(
                    (
                        "Synthetic postprocessor output is not validated for a real controller.",
                        "Bounded Level-2 evidence is not exact B-Rep, holder or kinematic validation.",
                        *level2.limitations,
                        *thread.limitations,
                    )
                )
            ),
            "unresolved_risks": ["R-049", "R-050", "R-051", "R-052"],
            "human_review_protocol": list(self.HUMAN_REVIEW_PROTOCOL),
            "external_validation_protocol": list(self.EXTERNAL_VALIDATION_PROTOCOL),
            "required_external_artifacts": list(self.REQUIRED_EXTERNAL_ARTIFACTS),
            "automatic_authority": False,
            "physical_use_authorized": False,
            "machine_send": False,
            "dnc": False,
            "nc_transfer": False,
            "cycle_start": False,
            "direct_machine_control": False,
            "human_review_bypass": False,
        }
