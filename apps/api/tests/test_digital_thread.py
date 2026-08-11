from __future__ import annotations

import hashlib
import json

import pytest
from starlette.testclient import TestClient

from app.modules.engineering.digital_thread import (
    BoundedManufacturingIntelligenceService,
    DigitalThreadError,
    DigitalThreadService,
    ORDER,
    SCHEMA_BY_TYPE,
)
from app.modules.engineering.digital_thread_schemas import (
    BoundedIntelligenceRequest,
    DigitalThreadBuildRequest,
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _payload(*, stale: bool = False) -> dict[str, object]:
    artifacts: list[dict[str, object]] = []
    previous = None
    for index, artifact_type in enumerate(ORDER):
        content = {"sequence": index, "type": artifact_type, "authority": "NON_PRODUCTION"}
        artifact_id = f"artifact-{index}"
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "schema_version": SCHEMA_BY_TYPE[artifact_type],
                "content": content,
                "declared_content_hash": _hash(content),
                "upstream_artifact_refs": [] if previous is None else [previous],
                "provenance": ["synthetic-v3-test"],
                "generation_metadata": {"rule": "deterministic"},
                "verification_refs": [] if index < 6 else ["bounded-evidence"],
                "lifecycle_status": "STALE" if stale and index == 4 else "CURRENT",
            }
        )
        previous = artifact_id
    return {"artifacts": artifacts}


def test_digital_thread_is_immutable_deterministic_and_complete() -> None:
    request = DigitalThreadBuildRequest.model_validate(_payload())
    first = DigitalThreadService().build(request, "organization-a")
    second = DigitalThreadService().build(request, "organization-a")

    assert first.schema_version == "vena-ia.digital-thread/v1"
    assert first.status == "COMPLETE_NON_PRODUCTION"
    assert first.replay_hash == second.replay_hash
    assert first.thread_id == second.thread_id
    assert first.missing_artifact_types == ()
    assert first.g9_state == "PENDING_AUTHORITATIVE_REVIEW"
    assert first.cad_to_gcode_controlled_validation_ready is False
    assert first.physical_use_authorized is False
    assert first.artifacts[0].downstream_artifact_refs == ("artifact-1",)


def test_digital_thread_rejects_hash_chain_version_and_stale_artifacts() -> None:
    mismatch = _payload()
    mismatch["artifacts"][2]["declared_content_hash"] = "0" * 64  # type: ignore[index]
    broken = _payload()
    broken["artifacts"][3]["upstream_artifact_refs"] = ["missing"]  # type: ignore[index]
    version = _payload()
    version["artifacts"][1]["schema_version"] = "forged/v99"  # type: ignore[index]

    for payload, message in (
        (mismatch, "hash"),
        (broken, "Upstream"),
        (version, "schema version"),
        (_payload(stale=True), "Stale"),
    ):
        with pytest.raises(DigitalThreadError, match=message):
            DigitalThreadService().build(
                DigitalThreadBuildRequest.model_validate(payload), "organization-a"
            )


def test_bounded_intelligence_is_read_only_and_detects_forged_manifest() -> None:
    thread = DigitalThreadService().build(
        DigitalThreadBuildRequest.model_validate(_payload()), "organization-a"
    )
    result = BoundedManufacturingIntelligenceService().analyze(
        BoundedIntelligenceRequest(thread=thread, mode="SUMMARIZE")
    )
    forged_artifact = thread.artifacts[0].model_copy(update={"content_hash": "0" * 64})
    forged = thread.model_copy(update={"artifacts": (forged_artifact, *thread.artifacts[1:])})
    rejected = BoundedManufacturingIntelligenceService().analyze(
        BoundedIntelligenceRequest(thread=forged, mode="EXPLAIN")
    )

    assert result.status == "AVAILABLE_FOR_HUMAN_REVIEW"
    assert result.read_only is True
    assert result.deterministic_evidence_mutated is False
    assert result.g9_state == "PENDING_AUTHORITATIVE_REVIEW"
    assert rejected.status == "BLOCKED_INVALID_EVIDENCE"


def _organization(client: TestClient, headers: dict[str, str], name: str) -> str:
    response = client.post("/organizations", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def test_digital_thread_routes_enforce_database_tenancy(
    client: TestClient,
    make_account,
) -> None:
    owner = make_account("thread-owner@vena-ia.dev")
    outsider = make_account("thread-outsider@vena-ia.dev")
    organization_id = _organization(client, owner.headers, "Thread owner")
    _organization(client, outsider.headers, "Thread outsider")
    url = f"/engineering/digital-thread?organization_id={organization_id}"

    assert client.post(url, json=_payload()).status_code == 401
    denied = client.post(url, headers=outsider.headers, json=_payload())
    allowed = client.post(url, headers=owner.headers, json=_payload())

    assert denied.status_code == 404
    assert allowed.status_code == 200, allowed.text
    manifest = allowed.json()
    intelligence = client.post(
        f"/engineering/digital-thread/intelligence?organization_id={organization_id}",
        headers=owner.headers,
        json={"thread": manifest, "mode": "SUMMARIZE"},
    )
    cross_org = client.post(
        f"/engineering/digital-thread/intelligence?organization_id={organization_id}",
        headers=outsider.headers,
        json={"thread": manifest, "mode": "SUMMARIZE"},
    )

    assert intelligence.status_code == 200, intelligence.text
    assert intelligence.json()["deterministic_evidence_mutated"] is False
    assert cross_org.status_code == 404
