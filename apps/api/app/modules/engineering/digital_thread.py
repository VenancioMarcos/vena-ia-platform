from __future__ import annotations

import hashlib
import json

from app.modules.engineering.digital_thread_schemas import (
    ArtifactType,
    BoundedIntelligenceRequest,
    BoundedIntelligenceResponse,
    DigitalThreadArtifact,
    DigitalThreadArtifactInput,
    DigitalThreadBuildRequest,
    DigitalThreadManifest,
)


ORDER: tuple[ArtifactType, ...] = (
    "CAD",
    "TOPOLOGY_EVIDENCE",
    "MANUFACTURING_GEOMETRY",
    "VERIFIED_PROCESS_PLAN",
    "TOOLPATH_CANDIDATE",
    "GCODE_CANDIDATE",
    "VERIFICATION_EVIDENCE",
    "REVIEW_STATE",
    "REPORT",
)
SCHEMA_BY_TYPE: dict[ArtifactType, str] = {
    "CAD": "vena-ia.cad-source/v1",
    "TOPOLOGY_EVIDENCE": "vena-ia.geometry-topology-evidence/v1",
    "MANUFACTURING_GEOMETRY": "vena-ia.manufacturing-geometry-model/v1",
    "VERIFIED_PROCESS_PLAN": "vena-ia.verified-process-plan/v1",
    "TOOLPATH_CANDIDATE": "vena-ia.toolpath-candidate/v1",
    "GCODE_CANDIDATE": "vena-ia.gcode-candidate/v1",
    "VERIFICATION_EVIDENCE": "vena-ia.level2-material-removal-evidence/v1",
    "REVIEW_STATE": "vena-ia.review-state/v1",
    "REPORT": "vena-ia.integrated-engineering-report/v1",
}


class DigitalThreadError(ValueError):
    pass


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class DigitalThreadService:
    def build(self, request: DigitalThreadBuildRequest, organization_id: str) -> DigitalThreadManifest:
        seen: dict[str, ArtifactType] = {}
        downstream: dict[str, list[str]] = {}
        drafts: list[tuple[DigitalThreadArtifactInput, str]] = []
        last_order = -1
        for source in request.artifacts:
            if source.artifact_id in seen:
                raise DigitalThreadError("Artifact IDs must be unique within a thread.")
            order = ORDER.index(source.artifact_type)
            if order < last_order:
                raise DigitalThreadError("Artifact chain order is invalid.")
            last_order = order
            if source.lifecycle_status != "CURRENT":
                raise DigitalThreadError("Stale or revoked artifacts fail closed.")
            if source.schema_version != SCHEMA_BY_TYPE[source.artifact_type]:
                raise DigitalThreadError("Artifact schema version does not match its type.")
            unknown = [reference for reference in source.upstream_artifact_refs if reference not in seen]
            if unknown:
                raise DigitalThreadError("Upstream artifact reference is missing or forward-pointing.")
            content_hash = _hash(source.content)
            if source.declared_content_hash and source.declared_content_hash != content_hash:
                raise DigitalThreadError("Declared artifact hash does not match canonical content.")
            for reference in source.upstream_artifact_refs:
                downstream.setdefault(reference, []).append(source.artifact_id)
            seen[source.artifact_id] = source.artifact_type
            drafts.append((source, content_hash))

        artifacts = tuple(
            DigitalThreadArtifact(
                artifact_id=source.artifact_id,
                artifact_type=source.artifact_type,
                schema_version=source.schema_version,
                content_hash=content_hash,
                organization_id=organization_id,
                upstream_artifact_refs=source.upstream_artifact_refs,
                downstream_artifact_refs=tuple(downstream.get(source.artifact_id, [])),
                provenance=source.provenance,
                generation_metadata=source.generation_metadata,
                replay_metadata={"canonical_content_hash": content_hash},
                verification_refs=source.verification_refs,
                limitations=(
                    "Immutable manifest evidence is non-production and requires human review.",
                ),
            )
            for source, content_hash in drafts
        )
        present = {artifact.artifact_type for artifact in artifacts}
        missing = tuple(item for item in ORDER if item not in present)
        replay_payload = {
            "organization_id": organization_id,
            "artifacts": [artifact.model_dump(mode="json") for artifact in artifacts],
            "missing": missing,
        }
        replay_hash = _hash(replay_payload)
        return DigitalThreadManifest(
            thread_id=f"thread-{replay_hash[:24]}",
            organization_id=organization_id,
            status=(
                "COMPLETE_NON_PRODUCTION"
                if not missing
                else "INCOMPLETE_REQUIRES_EVIDENCE"
            ),
            artifacts=artifacts,
            missing_artifact_types=missing,
            replay_hash=replay_hash,
            limitations=(
                "Manifest storage is caller-managed; no ledger or event store is implied.",
                "G9 remains an authoritative server-side human-review boundary.",
                "No artifact grants physical or production authority.",
            ),
        )


class BoundedManufacturingIntelligenceService:
    def analyze(self, request: BoundedIntelligenceRequest) -> BoundedIntelligenceResponse:
        thread = request.thread
        if not self._valid_manifest(thread) or (
            request.baseline is not None and not self._valid_manifest(request.baseline)
        ):
            return self._blocked("Manifest replay integrity validation failed.")
        if request.mode == "COMPARE" and request.baseline is None:
            return self._blocked("COMPARE requires a baseline manifest.")
        findings = [
            f"Thread {thread.thread_id} contains {len(thread.artifacts)} immutable artifact records.",
            f"Thread status is {thread.status} and G9 is {thread.g9_state}.",
        ]
        if request.baseline is not None:
            findings.append(
                "Replay hashes differ."
                if request.baseline.replay_hash != thread.replay_hash
                else "Replay hashes match."
            )
        missing = tuple(thread.missing_artifact_types)
        suggestions = (
            ("Supply missing evidence through authorized deterministic services.",)
            if missing
            else ("Submit the immutable evidence bundle for human review.",)
        )
        return BoundedIntelligenceResponse(
            status="AVAILABLE_FOR_HUMAN_REVIEW",
            explanation=(
                "Read-only bounded analysis of an immutable digital-thread manifest; "
                "deterministic evidence and review gates are not modified."
            ),
            findings=tuple(findings),
            missing_evidence=missing,
            suggestions=suggestions,
            limitations=(
                "This response is explanatory and cannot approve artifacts or G0-G9.",
                "No tool access, write capability or physical authority is present.",
            ),
        )

    @staticmethod
    def _blocked(reason: str) -> BoundedIntelligenceResponse:
        return BoundedIntelligenceResponse(
            status="BLOCKED_INVALID_EVIDENCE",
            explanation=reason,
            findings=(),
            missing_evidence=("baseline_manifest",),
            suggestions=("Provide a valid authorized baseline manifest.",),
            limitations=("No deterministic evidence was modified.",),
        )

    @staticmethod
    def _valid_manifest(thread: DigitalThreadManifest) -> bool:
        payload = {
            "organization_id": thread.organization_id,
            "artifacts": [artifact.model_dump(mode="json") for artifact in thread.artifacts],
            "missing": thread.missing_artifact_types,
        }
        replay = _hash(payload)
        return thread.replay_hash == replay and thread.thread_id == f"thread-{replay[:24]}"
