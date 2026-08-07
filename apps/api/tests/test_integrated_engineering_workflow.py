from copy import deepcopy
from unittest.mock import MagicMock

from starlette.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.features import FeatureDimension, FeatureRecognitionResult, GeometryFeature
from app.modules.cad.kernel import KernelGeometry
from app.modules.cad.parser import BoundingBox, StepAnalysis, StepParseError
from app.modules.cad.service import CADDocumentAnalysis
from app.modules.documents.dependencies import get_document_storage
from app.modules.organizations.models import Membership, Organization


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
            "source": "Controlled workflow test catalog",
            "properties": properties,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _analysis(feature_type: str = "THROUGH_CYLINDRICAL_HOLE") -> CADDocumentAnalysis:
    feature = GeometryFeature(
        feature_type=feature_type,
        confidence_class="HIGH_GEOMETRIC_EVIDENCE",
        geometry_evidence=("validated synthetic topology",),
        dimensions=(
            FeatureDimension("diameter", 10.0, "mm", "OCCT cylindrical surface"),
            FeatureDimension("depth", 25.0, "mm", "OCCT cylinder axial extent"),
        ),
        topology_refs=("face:1:LOCAL_ANALYSIS_REFERENCE",),
        assumptions=("Geometry does not establish manufacturing intent.",),
        limitations=("Human validation is required.",),
        sort_key=(feature_type,),
    )
    return CADDocumentAnalysis(
        document_id="document-001",
        source_filename="part.step",
        analysis=StepAnalysis(
            filename="part.step",
            schema="AP242",
            entity_count=12,
            entity_types={"ADVANCED_FACE": 6},
            cartesian_point_count=8,
            bounding_box=BoundingBox(
                minimum=(0.0, 0.0, 0.0),
                maximum=(100.0, 50.0, 25.0),
            ),
            length_unit="mm",
            volume=None,
            volume_status="UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL",
        ),
        report="Controlled analysis.",
        geometry=KernelGeometry(
            bounding_box=((0.0, 0.0, 0.0), (100.0, 50.0, 25.0)),
            surface_area=17_500.0,
            volume=125_000.0,
            topology_valid=True,
            shape_type="SOLID",
        ),
        features=FeatureRecognitionResult(
            status="AVAILABLE",
            features=(feature,),
            warnings=(),
            limitations=("Validated synthetic corpus boundary.",),
            uncertainty="VALIDATED_SYNTHETIC_CORPUS_BOUNDARY",
            tolerance=1e-6,
        ),
    )


def _full_payload(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    material_id = _catalog(
        client,
        headers,
        "MATERIAL",
        "AL-6061-WF",
        {"cutting_speed_m_min": 150, "feed_per_tooth_mm": 0.05},
    )
    machine_id = _catalog(
        client,
        headers,
        "MACHINE",
        "MILL-WF",
        {"operations": ["drilling"], "max_rpm": 10_000, "max_feed_mm_min": 4_000},
    )
    tool_id = _catalog(
        client,
        headers,
        "TOOL",
        "DRILL-WF",
        {"operations": ["drilling"], "diameter_mm": 10, "teeth": 2},
    )
    return {
        "document_id": "document-001",
        "feature_id": "feature-0001",
        "material_id": material_id,
        "machine_id": machine_id,
        "tool_id": tool_id,
        "manufacturing_intent": "Preliminary drilling candidate review",
        "drawing_tolerance": "+/- 0.05 mm",
        "surface_finish": "Ra 3.2 um",
        "fixture": "Human-reviewed vise assumption",
        "coolant": "Flood coolant assumption",
        "material_condition": "T6",
        "setup_time_min": 15,
        "machine_hour_rate": 100,
        "currency": "BRL",
        "tool_number": 7,
        "clearance_z_mm": 20,
    }


def _without_timestamps(value: dict[str, object]) -> dict[str, object]:
    result = deepcopy(value)
    result.pop("generated_at", None)
    engineering = result.get("engineering")
    if isinstance(engineering, dict):
        engineering.pop("generated_at", None)
    review = result.get("integrated_report")
    if isinstance(review, dict):
        engineering_review = review.get("engineering_review")
        if isinstance(engineering_review, dict):
            engineering_review.pop("generated_at", None)
    return result


def test_integrated_workflow_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/engineering/workflows",
        json={"document_id": "document-001", "feature_id": "feature-0001"},
    )
    assert response.status_code == 401


def test_integrated_workflow_reuses_analysis_and_is_deterministic(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("workflow@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.return_value = _analysis()
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        payload = _full_payload(client, account.headers)
        first = client.post("/engineering/workflows", headers=account.headers, json=payload)
        second = client.post("/engineering/workflows", headers=account.headers, json=payload)
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert first.status_code == second.status_code == 200, first.text
    left, right = first.json(), second.json()
    assert _without_timestamps(left) == _without_timestamps(right)
    assert left["workflow_status"] == "COMPLETE_PRELIMINARY"
    assert left["schema_version"] == "vena-ia.integrated-engineering-workflow/v1"
    assert left["planning"]["planning_candidates"][0]["status"] == "POSSIBLE_NOT_SELECTED"
    assert left["cnc_neutral_plan"]["schema_version"] == "vena-ia.cnc-neutral-plan/v1"
    assert left["cnc_neutral_plan"]["simulation_only"] is True
    assert left["cnc_neutral_plan"]["executable_output"] is False
    assert left["review_status"] == "REQUIRES_HUMAN_REVIEW"
    assert left["integrated_report"]["status"] == "REQUIRES_HUMAN_REVIEW"
    assert cad.analyze.call_count == 2
    serialized = first.text.lower()
    assert "production_ready" not in serialized
    assert "machine_ready" not in serialized
    assert "approved_for_manufacturing" not in serialized


def test_missing_inputs_remain_explicit_and_block_cnc(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("workflow-missing@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.return_value = _analysis()
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        response = client.post(
            "/engineering/workflows",
            headers=account.headers,
            json={"document_id": "document-001", "feature_id": "feature-0001"},
        )
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_status"] == "BLOCKED_MISSING_INPUT"
    assert body["cnc_neutral_plan"] is None
    assert {
        "material",
        "machine",
        "tool",
        "drawing_tolerance",
        "fixture",
        "tool_number",
        "clearance_z_mm",
    }.issubset(body["missing_inputs"])


def test_unsupported_feature_never_escalates_to_process(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("workflow-unsupported@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.return_value = _analysis("PLANAR_FACE")
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        payload = _full_payload(client, account.headers)
        response = client.post("/engineering/workflows", headers=account.headers, json=payload)
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_status"] == "BLOCKED_UNSUPPORTED_FEATURE"
    assert body["planning"]["planning_candidates"] == []
    assert body["cnc_neutral_plan"] is None


def test_incompatible_catalog_selection_remains_partial(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("workflow-incompatible@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.return_value = _analysis()
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        payload = _full_payload(client, account.headers)
        incompatible_machine = _catalog(
            client,
            account.headers,
            "MACHINE",
            "MILL-INCOMPATIBLE",
            {"operations": ["milling"], "max_rpm": 10_000, "max_feed_mm_min": 4_000},
        )
        payload["machine_id"] = incompatible_machine
        response = client.post("/engineering/workflows", headers=account.headers, json=payload)
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_status"] == "PARTIAL"
    assert body["engineering"]["compatibility"].endswith("INCOMPATIBLE")
    assert body["cnc_neutral_plan"] is None


def test_workflow_rejects_executable_and_authority_fields(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("workflow-negative@vena-ia.dev")
    for forbidden in ("gcode", "mcode", "toolpath", "organization_id", "owner_id"):
        payload = {
            "document_id": "document-001",
            "feature_id": "feature-0001",
            forbidden: "forged",
        }
        assert client.post(
            "/engineering/workflows",
            headers=account.headers,
            json=payload,
        ).status_code == 422


def test_invalid_cad_failure_is_preserved(client: TestClient, make_account) -> None:
    account = make_account("workflow-invalid-cad@vena-ia.dev")
    cad = MagicMock()
    cad.analyze.side_effect = StepParseError("invalid STEP evidence")
    app.dependency_overrides[get_cad_analysis_service] = lambda: cad
    try:
        response = client.post(
            "/engineering/workflows",
            headers=account.headers,
            json={"document_id": "document-001", "feature_id": "feature-0001"},
        )
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)
    assert response.status_code == 422
    assert response.json() == {"detail": "invalid STEP evidence"}


def test_cross_user_document_is_hidden_before_storage_access(
    client: TestClient,
    make_account,
) -> None:
    storage = MagicMock()
    storage.download_file.return_value = b"not reached"
    app.dependency_overrides[get_document_storage] = lambda: storage
    try:
        owner = make_account("workflow-owner@vena-ia.dev")
        project = client.post(
            "/projects", headers=owner.headers, json={"name": "Private workflow"}
        ).json()
        uploaded = client.post(
            f"/projects/{project['id']}/documents",
            headers=owner.headers,
            files={
                "file": (
                    "part.step",
                    b"ISO-10303-21;\nEND-ISO-10303-21;",
                    "application/step",
                )
            },
        ).json()
        outsider = make_account("workflow-outsider@vena-ia.dev")
        response = client.post(
            "/engineering/workflows",
            headers=outsider.headers,
            json={"document_id": uploaded["id"], "feature_id": "feature-0001"},
        )
    finally:
        app.dependency_overrides.pop(get_document_storage, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
    storage.download_file.assert_not_called()


def test_cross_org_membership_does_not_bypass_document_ownership(
    client: TestClient,
    make_account,
    db_session,
) -> None:
    owner = make_account("workflow-org-a@vena-ia.dev")
    outsider = make_account("workflow-org-b@vena-ia.dev")
    db_session.add_all(
        [
            Organization(id="org-a", name="Organization A"),
            Organization(id="org-b", name="Organization B"),
            Membership(
                id="membership-a",
                organization_id="org-a",
                user_id=owner.id,
                team_id=None,
                role="OWNER",
                status="ACTIVE",
                created_by=owner.id,
            ),
            Membership(
                id="membership-b",
                organization_id="org-b",
                user_id=outsider.id,
                team_id=None,
                role="OWNER",
                status="ACTIVE",
                created_by=outsider.id,
            ),
        ]
    )
    db_session.commit()
    storage = MagicMock()
    storage.download_file.return_value = b"not reached"
    app.dependency_overrides[get_document_storage] = lambda: storage
    try:
        project = client.post(
            "/projects", headers=owner.headers, json={"name": "Organization A project"}
        ).json()
        uploaded = client.post(
            f"/projects/{project['id']}/documents",
            headers=owner.headers,
            files={
                "file": (
                    "part.step",
                    b"ISO-10303-21;\nEND-ISO-10303-21;",
                    "application/step",
                )
            },
        ).json()
        response = client.post(
            "/engineering/workflows",
            headers=outsider.headers,
            json={"document_id": uploaded["id"], "feature_id": "feature-0001"},
        )
    finally:
        app.dependency_overrides.pop(get_document_storage, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
    storage.download_file.assert_not_called()


def test_openapi_contract_is_closed_and_non_executable(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/engineering/workflows"]["post"]
    request_ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    request_name = request_ref.rsplit("/", 1)[-1]
    request_properties = schema["components"]["schemas"][request_name]["properties"]
    assert not {
        "gcode",
        "mcode",
        "toolpath",
        "nc_file",
        "transmission_target",
        "organization_id",
        "owner_id",
        "user_id",
    }.intersection(request_properties)
    statuses = schema["components"]["schemas"]["WorkflowStatus"]["enum"]
    assert statuses == [
        "COMPLETE_PRELIMINARY",
        "PARTIAL",
        "BLOCKED_MISSING_INPUT",
        "BLOCKED_UNSUPPORTED_FEATURE",
        "FAILED",
    ]
