from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import asdict
from typing import cast

from pydantic import JsonValue

from app.modules.cad.evidence import GeometryTopologyEvidence
from app.modules.cad.service import CADAnalysisService, CADDocumentAnalysis
from app.modules.engineering.blind_validation import ControlledBlindValidationService
from app.modules.engineering.blind_validation_schemas import (
    ControlledBlindValidationEvidence,
    ControlledBlindValidationRequest,
)
from app.modules.engineering.controlled_environment_schemas import (
    ControlledDownloadRequest,
    ControlledEnvironmentRequest,
    ControlledEnvironmentResult,
)
from app.modules.engineering.digital_thread import DigitalThreadService
from app.modules.engineering.digital_thread_schemas import (
    ArtifactType,
    DigitalThreadArtifactInput,
    DigitalThreadBuildRequest,
    DigitalThreadManifest,
)
from app.modules.engineering.level2 import Level2Verifier
from app.modules.engineering.level2_schemas import (
    Level2VerificationEvidence,
    Level2VerificationRequest,
)
from app.modules.engineering.manufacturing import ManufacturingPlanningService
from app.modules.engineering.manufacturing_schemas import ManufacturingGeometryModel
from app.modules.engineering.postprocessor import RS274SafeSubsetVerifier, SyntheticPostprocessor
from app.modules.engineering.postprocessor_schemas import GCodeCandidate, GCodeCandidateRequest
from app.modules.engineering.service import EngineeringCatalogService
from app.modules.engineering.toolpath import ToolpathCandidateService
from app.modules.engineering.toolpath_schemas import ToolpathCandidate, ToolpathCandidateRequest


class ControlledEnvironmentError(ValueError):
    pass


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class _PreloadedCAD:
    def __init__(self, document_id: str, analysis: CADDocumentAnalysis) -> None:
        self.document_id = document_id
        self.analysis = analysis

    def analyze(self, document_id: str) -> CADDocumentAnalysis:
        if document_id != self.document_id:
            raise ControlledEnvironmentError("CAD document reference changed during orchestration.")
        return self.analysis


class ControlledEnvironmentService:
    """Orchestrates existing deterministic services without granting physical authority."""

    def __init__(
        self,
        cad: CADAnalysisService,
        engineering: EngineeringCatalogService,
        signing_key: str,
    ) -> None:
        if len(signing_key.encode()) < 32:
            raise ControlledEnvironmentError("Controlled download signing key is unavailable.")
        self.cad = cad
        self.engineering = engineering
        self.signing_key = signing_key.encode()

    def run(
        self, request: ControlledEnvironmentRequest, user_id: str
    ) -> ControlledEnvironmentResult:
        self._require_catalog_scope(request)
        analysis = self.cad.analyze(request.planning.document_id)
        if analysis.topology_evidence is None:
            raise ControlledEnvironmentError("Topology evidence is unavailable.")
        cad_hash = analysis.topology_evidence.source_sha256
        model = ManufacturingPlanningService(
            _PreloadedCAD(request.planning.document_id, analysis),  # type: ignore[arg-type]
            self.engineering,
        ).plan(request.planning)
        operation = next(
            (
                item
                for item in model.operation_candidates
                if item.status == "CANDIDATE_REQUIRES_HUMAN_REVIEW"
            ),
            None,
        )
        if operation is None:
            raise ControlledEnvironmentError("No reviewed operation candidate is available.")
        toolpath = ToolpathCandidateService().create(
            ToolpathCandidateRequest(
                manufacturing_model=model,
                operation_candidate_id=operation.candidate_id,
                tool=request.tool,
                machine_minimum=request.machine_minimum,
                machine_maximum=request.machine_maximum,
                clearance_z_mm=request.clearance_z_mm,
                retract_z_mm=request.retract_z_mm,
                feed_mm_min=request.feed_mm_min,
            )
        )
        gcode = SyntheticPostprocessor().generate(GCodeCandidateRequest(toolpath=toolpath))
        level2 = Level2Verifier().verify(
            Level2VerificationRequest(
                manufacturing_model=model,
                toolpath=toolpath,
                fixture_keep_outs=request.fixture_keep_outs,
            )
        )
        blind = ControlledBlindValidationService().freeze(
            ControlledBlindValidationRequest(
                holdout_id=request.holdout_id,
                sealed_reference_hash=request.sealed_reference_hash,
                cad_hash=cad_hash,
                manufacturing_model=model,
                toolpath=toolpath,
                gcode_candidate=gcode,
                level2_evidence=level2,
                questions_asked=request.questions_asked,
            )
        )
        if not ControlledBlindValidationService.validate(blind):
            raise ControlledEnvironmentError("Controlled validation evidence failed closed.")
        thread = self._thread(
            request.organization_id,
            analysis,
            analysis.topology_evidence,
            model,
            toolpath,
            gcode,
            level2,
            blind,
        )
        token = self._token(
            user_id,
            request.organization_id,
            _hash(gcode.model_dump(mode="json")),
            _hash(thread.model_dump(mode="json")),
            _hash(blind.model_dump(mode="json")),
        )
        return ControlledEnvironmentResult(
            status="READY_FOR_CONTROLLED_DOWNLOAD",
            manufacturing_model=model,
            toolpath=toolpath,
            gcode_candidate=gcode,
            level2_evidence=level2,
            blind_validation=blind,
            digital_thread=thread,
            download_token=token,
            limitations=[
                "Controlled download is a non-production candidate export only.",
                "External machine simulation and authoritative G9 review remain required.",
                "No machine-send, DNC, NC transfer, cycle start or machine control exists.",
            ],
        )

    def validate_download(self, request: ControlledDownloadRequest, user_id: str) -> str:
        claims = self._verify_token(request.download_token)
        expected = {
            "sub": user_id,
            "org": request.organization_id,
            "gcode": _hash(request.gcode_candidate.model_dump(mode="json")),
            "thread": _hash(request.digital_thread.model_dump(mode="json")),
            "blind": _hash(request.blind_validation.model_dump(mode="json")),
        }
        if any(claims.get(key) != value for key, value in expected.items()):
            raise ControlledEnvironmentError(
                "Controlled download proof does not match the artifacts."
            )
        expires_at = claims.get("exp")
        if not isinstance(expires_at, int) or expires_at < int(time.time()):
            raise ControlledEnvironmentError("Controlled download proof expired.")
        candidate = request.gcode_candidate
        if hashlib.sha256(candidate.program.encode()).hexdigest() != candidate.output_hash:
            raise ControlledEnvironmentError("Candidate G-code hash mismatch.")
        if candidate.manifest.get("output_hash") != candidate.output_hash:
            raise ControlledEnvironmentError("Candidate G-code manifest mismatch.")
        if candidate.manifest.get("toolpath_hash") != candidate.source_toolpath_hash:
            raise ControlledEnvironmentError("Candidate toolpath binding mismatch.")
        verification = RS274SafeSubsetVerifier().verify(
            candidate.program, candidate.source_toolpath_hash
        )
        if verification.status != "PASS_REQUIRES_HUMAN_REVIEW":
            raise ControlledEnvironmentError("Candidate G-code failed independent verification.")
        if verification != candidate.verification:
            raise ControlledEnvironmentError("Candidate verification replay mismatch.")
        if candidate.production_authority or candidate.executable_output:
            raise ControlledEnvironmentError("Production or executable authority is forbidden.")
        blind = request.blind_validation
        if not ControlledBlindValidationService.validate(blind):
            raise ControlledEnvironmentError("Controlled validation evidence failed closed.")
        if blind.frozen_artifact_hashes.get("gcode_candidate") != candidate.output_hash:
            raise ControlledEnvironmentError("Controlled evidence G-code binding mismatch.")
        if request.digital_thread.organization_id != request.organization_id:
            raise ControlledEnvironmentError("Digital Thread organization mismatch.")
        thread = request.digital_thread
        if (
            thread.status != "COMPLETE_NON_PRODUCTION"
            or thread.missing_artifact_types
            or thread.cad_to_gcode_controlled_validation_ready
            or thread.physical_use_authorized
        ):
            raise ControlledEnvironmentError("Digital Thread safety state is invalid.")
        if not DigitalThreadService().validate(thread):
            raise ControlledEnvironmentError("Digital Thread replay integrity failed.")
        artifacts = {item.artifact_type: item for item in thread.artifacts}
        if artifacts.get("GCODE_CANDIDATE") is None or (
            artifacts["GCODE_CANDIDATE"].content_hash != _hash(candidate.model_dump(mode="json"))
        ):
            raise ControlledEnvironmentError("Digital Thread G-code binding mismatch.")
        if artifacts.get("REPORT") is None or (
            artifacts["REPORT"].content_hash != _hash(blind.model_dump(mode="json"))
        ):
            raise ControlledEnvironmentError("Digital Thread report binding mismatch.")
        return candidate.program

    def _require_catalog_scope(self, request: ControlledEnvironmentRequest) -> None:
        for item_id in (
            request.planning.material_id,
            request.planning.machine_id,
            request.planning.tool_id,
        ):
            if item_id is None:
                continue
            item = self.engineering.repository.get(item_id)
            if item is None or (
                item.scope_type == "ORGANIZATION_OWNED"
                and item.organization_id != request.organization_id
            ):
                raise ControlledEnvironmentError(
                    "Catalog item does not belong to the controlled organization."
                )

    def _thread(
        self,
        organization_id: str,
        analysis: CADDocumentAnalysis,
        topology: GeometryTopologyEvidence,
        manufacturing: ManufacturingGeometryModel,
        path: ToolpathCandidate,
        candidate: GCodeCandidate,
        verification: Level2VerificationEvidence,
        report: ControlledBlindValidationEvidence,
    ) -> DigitalThreadManifest:
        sources: list[tuple[str, ArtifactType, str, dict[str, JsonValue]]] = [
            (
                "cad",
                "CAD",
                "vena-ia.cad-source/v1",
                {
                    "document_id": analysis.document_id,
                    "filename": analysis.source_filename,
                    "sha256": manufacturing.final_geometry.source_geometry_hash,
                },
            ),
            (
                "topology",
                "TOPOLOGY_EVIDENCE",
                manufacturing.final_geometry.topology_evidence_schema,
                cast(
                    dict[str, JsonValue],
                    json.loads(json.dumps(asdict(topology), separators=(",", ":"))),
                ),
            ),
            (
                "manufacturing",
                "MANUFACTURING_GEOMETRY",
                manufacturing.schema_version,
                cast(dict[str, JsonValue], manufacturing.model_dump(mode="json")),
            ),
            (
                "process-plan",
                "VERIFIED_PROCESS_PLAN",
                manufacturing.planning_schema_version,
                cast(dict[str, JsonValue], manufacturing.verification.model_dump(mode="json")),
            ),
            (
                "toolpath",
                "TOOLPATH_CANDIDATE",
                path.schema_version,
                cast(dict[str, JsonValue], path.model_dump(mode="json")),
            ),
            (
                "gcode",
                "GCODE_CANDIDATE",
                candidate.schema_version,
                cast(dict[str, JsonValue], candidate.model_dump(mode="json")),
            ),
            (
                "verification",
                "VERIFICATION_EVIDENCE",
                verification.schema_version,
                cast(dict[str, JsonValue], verification.model_dump(mode="json")),
            ),
            (
                "review",
                "REVIEW_STATE",
                "vena-ia.review-state/v1",
                {"g9": "PENDING_AUTHORITATIVE_REVIEW", "physical_use_authorized": False},
            ),
            (
                "report",
                "REPORT",
                "vena-ia.integrated-engineering-report/v1",
                cast(dict[str, JsonValue], report.model_dump(mode="json")),
            ),
        ]
        artifacts = []
        previous = None
        for artifact_id, artifact_type, schema, content in sources:
            artifacts.append(
                DigitalThreadArtifactInput(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    schema_version=schema,
                    content=content,
                    upstream_artifact_refs=(() if previous is None else (previous,)),
                    provenance=("TASK-V31-002",),
                )
            )
            previous = artifact_id
        return DigitalThreadService().build(
            DigitalThreadBuildRequest(artifacts=tuple(artifacts)), organization_id
        )

    def _token(
        self, user_id: str, organization_id: str, gcode: str, thread: str, blind: str
    ) -> str:
        payload = json.dumps(
            {
                "sub": user_id,
                "org": organization_id,
                "gcode": gcode,
                "thread": thread,
                "blind": blind,
                "exp": int(time.time()) + 900,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        body = base64.urlsafe_b64encode(payload).rstrip(b"=")
        signature = base64.urlsafe_b64encode(
            hmac.new(self.signing_key, body, hashlib.sha256).digest()
        ).rstrip(b"=")
        return f"{body.decode()}.{signature.decode()}"

    def _verify_token(self, token: str) -> dict[str, object]:
        try:
            encoded, provided = token.split(".", 1)
            body = encoded.encode()
            expected = (
                base64.urlsafe_b64encode(hmac.new(self.signing_key, body, hashlib.sha256).digest())
                .rstrip(b"=")
                .decode()
            )
            if not hmac.compare_digest(provided, expected):
                raise ControlledEnvironmentError("Controlled download proof signature is invalid.")
            padding = "=" * (-len(encoded) % 4)
            claims = json.loads(base64.urlsafe_b64decode(encoded + padding))
            if not isinstance(claims, dict):
                raise ControlledEnvironmentError("Controlled download proof is malformed.")
            return cast(dict[str, object], claims)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ControlledEnvironmentError("Controlled download proof is malformed.") from exc
