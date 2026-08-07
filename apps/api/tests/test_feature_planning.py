from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.features import (
    FeatureDimension,
    FeatureRecognitionResult,
    GeometryFeature,
    REVIEW_STATUS,
)
from app.modules.documents.service import DocumentAccessDeniedError


def _feature(feature_type: str) -> GeometryFeature:
    dimensions = (
        FeatureDimension("diameter", 4.0, "mm", "synthetic corpus"),
        FeatureDimension("depth", 30.0, "mm", "synthetic corpus"),
    )
    return GeometryFeature(
        feature_type=feature_type,
        confidence_class="HIGH_GEOMETRIC_EVIDENCE",
        geometry_evidence=("validated synthetic topology",),
        dimensions=dimensions,
        topology_refs=("face:7:LOCAL_ANALYSIS_REFERENCE",),
        assumptions=("geometric evidence only",),
        limitations=("no manufacturing intent",),
        sort_key=(feature_type,),
    )


def _cad_service(*features: GeometryFeature) -> MagicMock:
    cad = MagicMock()
    cad.analyze.return_value = SimpleNamespace(
        document_id="document",
        features=FeatureRecognitionResult(
            status="AVAILABLE",
            features=features,
            warnings=(),
            limitations=("human review",),
            uncertainty="VALIDATED_SYNTHETIC_CORPUS_BOUNDARY",
            tolerance=1e-6,
        ),
    )
    return cad


def _post(
    client: TestClient,
    headers: dict[str, str],
    cad: MagicMock,
    payload: dict[str, object],
):
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        return client.post(
            "/engineering/planning/from-document-feature",
            headers=headers,
            json=payload,
        )
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)


def _catalog(
    client: TestClient,
    headers: dict[str, str],
    kind: str,
    code: str,
    properties: dict[str, object],
) -> str:
    response = client.post(
        "/engineering/catalogs",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": code,
            "data_version": "2026.08",
            "source": "Synthetic planning fixture",
            "properties": properties,
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_feature_planning_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/engineering/planning/from-document-feature",
        json={"document_id": "document", "feature_id": "feature-0001"},
    )
    assert response.status_code == 401


def test_through_hole_produces_only_non_executable_drilling_candidate(
    client: TestClient, make_account
) -> None:
    account = make_account(email="feature-planner@vena-ia.dev")
    response = _post(
        client,
        account.headers,
        _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE")),
        {"document_id": "document", "feature_id": "feature-0001"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["schema_version"] == "vena-ia.feature-planning/v1"
    assert body["status"] == "REQUIRED_INPUT"
    assert body["review_status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert body["planning_rule_version"] == "1.0.0"
    assert body["planning_candidates"] == [
        {
            "candidate_type": "DRILLING_CANDIDATE",
            "operation": "drilling",
            "status": "POSSIBLE_NOT_SELECTED",
            "evidence": [
                "Validated feature type is THROUGH_CYLINDRICAL_HOLE.",
                "validated synthetic topology",
            ],
            "executable_output": False,
        }
    ]
    assert {"material", "machine", "tool"}.issubset(body["unavailable_inputs"])
    assert body["engineering_recommendation"] is None
    candidate_text = str(body["planning_candidates"]).lower()
    assert "g-code" not in candidate_text
    assert "toolpath" not in candidate_text
    assert "coordinate" not in candidate_text
    assert "manufacturable" not in candidate_text


def test_primitives_and_blind_or_ambiguous_context_produce_no_candidate(
    client: TestClient, make_account
) -> None:
    account = make_account(email="no-false-planning@vena-ia.dev")
    for feature_type in ("PLANAR_FACE", "CYLINDRICAL_FACE", "AMBIGUOUS"):
        response = _post(
            client,
            account.headers,
            _cad_service(_feature(feature_type)),
            {"document_id": "document", "feature_id": "feature-0001"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NO_PLANNING_CANDIDATE"
        assert response.json()["planning_candidates"] == []


def test_bridge_reuses_engineering_recommendation_only_with_explicit_catalogs(
    client: TestClient, make_account
) -> None:
    account = make_account(email="planning-catalogs@vena-ia.dev")
    material_id = _catalog(
        client,
        account.headers,
        "MATERIAL",
        "PLAN-MAT",
        {"cutting_speed_m_min": 80, "feed_per_tooth_mm": 0.04},
    )
    machine_id = _catalog(
        client,
        account.headers,
        "MACHINE",
        "PLAN-MACHINE",
        {"operations": ["drilling"], "max_rpm": 6000, "max_feed_mm_min": 1000},
    )
    tool_id = _catalog(
        client,
        account.headers,
        "TOOL",
        "PLAN-DRILL",
        {"operations": ["drilling"], "diameter_mm": 4, "teeth": 2},
    )
    response = _post(
        client,
        account.headers,
        _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE")),
        {
            "document_id": "document",
            "feature_id": "feature-0001",
            "material_id": material_id,
            "machine_id": machine_id,
            "tool_id": tool_id,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "PRELIMINARY_PLANNING_AVAILABLE"
    assert body["engineering_recommendation"]["schema_version"] == (
        "vena-ia.engineering-recommendation/v1"
    )
    assert body["engineering_recommendation"]["operation"] == "drilling"
    assert body["engineering_recommendation"]["status"] == (
        "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    )
    assert "engineering-rule:engineering-rule/v1.0.0" in body["traceability"]

    replay = _post(
        client,
        account.headers,
        _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE")),
        {
            "document_id": "document",
            "feature_id": "feature-0001",
            "material_id": material_id,
            "machine_id": machine_id,
            "tool_id": tool_id,
        },
    )
    assert replay.json() == body


def test_planning_replay_is_deterministic_without_catalogs(client: TestClient, make_account) -> None:
    account = make_account(email="planning-replay@vena-ia.dev")
    cad = _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE"))
    payload = {"document_id": "document", "feature_id": "feature-0001"}
    first = _post(client, account.headers, cad, payload)
    second = _post(client, account.headers, cad, payload)
    assert first.json() == second.json()


@pytest.mark.parametrize(
    "supplied",
    [
        {"material_id": "material"},
        {"material_id": "material", "machine_id": "machine"},
        {"machine_id": "machine", "tool_id": "tool"},
    ],
)
def test_incomplete_catalog_selection_never_calls_recommendation(
    client: TestClient, make_account, supplied: dict[str, str]
) -> None:
    account = make_account()
    response = _post(
        client,
        account.headers,
        _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE")),
        {"document_id": "document", "feature_id": "feature-0001", **supplied},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["engineering_recommendation"] is None
    assert body["status"] == "REQUIRED_INPUT"
    assert any(name in body["unavailable_inputs"] for name in ("material", "machine", "tool"))


def test_feature_count_resource_limit_fails_closed(client: TestClient, make_account) -> None:
    account = make_account(email="planning-limit@vena-ia.dev")
    features = tuple(_feature("PLANAR_FACE") for _index in range(101))
    response = _post(
        client,
        account.headers,
        _cad_service(*features),
        {"document_id": "document", "feature_id": "feature-0001"},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Feature planning resource limit exceeded"}


def test_empty_catalog_reference_is_rejected(client: TestClient, make_account) -> None:
    account = make_account(email="planning-empty-id@vena-ia.dev")
    response = _post(
        client,
        account.headers,
        _cad_service(_feature("THROUGH_CYLINDRICAL_HOLE")),
        {
            "document_id": "document",
            "feature_id": "feature-0001",
            "material_id": "",
        },
    )
    assert response.status_code == 422


def test_feature_reference_and_evidence_fail_closed(client: TestClient, make_account) -> None:
    account = make_account(email="planning-invalid@vena-ia.dev")
    missing = _post(
        client,
        account.headers,
        _cad_service(_feature("PLANAR_FACE")),
        {"document_id": "document", "feature_id": "feature-0002"},
    )
    assert missing.status_code == 404

    invalid = _feature("THROUGH_CYLINDRICAL_HOLE")
    invalid = GeometryFeature(
        **{**invalid.__dict__, "review_status": "UNREVIEWED"}
    )
    rejected = _post(
        client,
        account.headers,
        _cad_service(invalid),
        {"document_id": "document", "feature_id": "feature-0001"},
    )
    assert rejected.status_code == 422


def test_cross_user_document_failure_is_hidden(client: TestClient, make_account) -> None:
    account = make_account(email="planning-outsider@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.side_effect = DocumentAccessDeniedError("denied")
    response = _post(
        client,
        account.headers,
        cad,
        {"document_id": "other-document", "feature_id": "feature-0001"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
    assert REVIEW_STATUS == "PRELIMINARY_GEOMETRIC_FEATURE_REQUIRES_HUMAN_REVIEW"
