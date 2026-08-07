from starlette.testclient import TestClient
from sqlalchemy import select

from app.modules.audit.models import SecurityAuditEvent
from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.organizations.models import Membership, Team


def _organization(client: TestClient, headers: dict[str, str]) -> str:
    listed = client.get("/organizations", headers=headers)
    assert listed.status_code == 200, listed.text
    if listed.json():
        return str(listed.json()[0]["id"])
    created = client.post(
        "/organizations", headers=headers, json={"name": "Engineering test organization"}
    )
    assert created.status_code == 201, created.text
    return str(created.json()["id"])


def _create(
    client: TestClient,
    headers: dict[str, str],
    kind: str,
    code: str,
    properties: dict[str, object] | None = None,
) -> dict[str, object]:
    organization_id = _organization(client, headers)
    response = client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": f"Test {kind}",
            "data_version": "2026.08",
            "source": "Owner-supplied engineering catalog fixture",
            "properties": properties or {"unit_system": "METRIC"},
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_catalog_requires_authentication(client: TestClient) -> None:
    assert client.get("/engineering/catalogs").status_code == 401


def test_versioned_catalog_and_preliminary_selection(client: TestClient, make_account) -> None:
    account = make_account()
    material = _create(client, account.headers, "MATERIAL", "AL-6061-T6")
    machine = _create(client, account.headers, "MACHINE", "MILL-001")
    tool = _create(client, account.headers, "TOOL", "EM-10-4F")

    organization_id = _organization(client, account.headers)
    listed = client.get(
        f"/engineering/catalogs?organization_id={organization_id}&kind=MATERIAL",
        headers=account.headers,
    )
    assert listed.status_code == 200
    assert [item["code"] for item in listed.json()] == ["AL-6061-T6"]
    assert listed.json()[0]["schema_version"] == "vena-ia.engineering-catalog/v1"

    selected = client.post(
        "/engineering/selections/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "MILLING",
        },
    )
    assert selected.status_code == 200, selected.text
    body = selected.json()
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert len(body["traceability"]) == 3
    assert "G-code" in body["limitations"][0]


def test_selection_rejects_wrong_catalog_kind(client: TestClient, make_account) -> None:
    account = make_account(email="other@vena-ia.dev")
    material = _create(client, account.headers, "MATERIAL", "STEEL-1018")
    response = client.post(
        "/engineering/selections/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": material["id"],
            "tool_id": material["id"],
            "operation": "MILLING",
        },
    )
    assert response.status_code == 404


def test_deterministic_recommendation_time_cost_and_limits(
    client: TestClient, make_account
) -> None:
    account = make_account(email="engineer@vena-ia.dev")
    material = _create(
        client,
        account.headers,
        "MATERIAL",
        "AL-7075",
        {"cutting_speed_m_min": 180, "feed_per_tooth_mm": 0.05},
    )
    machine = _create(
        client,
        account.headers,
        "MACHINE",
        "MILL-002",
        {"operations": ["milling"], "max_rpm": 12000, "max_feed_mm_min": 5000},
    )
    tool = _create(
        client,
        account.headers,
        "TOOL",
        "EM-8-4F",
        {"operations": ["milling"], "diameter_mm": 8, "teeth": 4},
    )
    response = client.post(
        "/engineering/recommendations/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "milling",
            "cutting_length_mm": 1000,
            "setup_time_min": 15,
            "machine_hour_rate": 120,
            "tool_cost_allocation": 5,
            "currency": "BRL",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["schema_version"] == "vena-ia.engineering-recommendation/v1"
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert body["compatibility"] == "PRELIMINARY_COMPATIBILITY_CHECK:COMPATIBLE"
    assert body["preliminary_parameters"]["spindle_speed"]["unit"] == "rpm"
    assert body["machining_time_estimate"]["status"] == "AVAILABLE"
    assert body["cost_estimate"]["unit"] == "BRL"
    assert "G-code" in body["limitations"][2]
    assert "coordinates" not in str(body).lower()


def test_recommendation_reports_not_available_without_properties(
    client: TestClient, make_account
) -> None:
    account = make_account(email="limited@vena-ia.dev")
    material = _create(client, account.headers, "MATERIAL", "UNKNOWN-MAT")
    machine = _create(client, account.headers, "MACHINE", "UNKNOWN-MACHINE")
    tool = _create(client, account.headers, "TOOL", "UNKNOWN-TOOL")
    response = client.post(
        "/engineering/recommendations/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "drilling",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["preliminary_parameters"]["spindle_speed"]["status"] == "NOT_AVAILABLE"
    assert body["cost_estimate"]["status"] == "NOT_AVAILABLE"
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"


def test_recommendation_requires_authentication(client: TestClient) -> None:
    assert client.post("/engineering/recommendations/preliminary", json={}).status_code == 401


def test_review_report_is_reproducible_and_never_authorizes_cnc(
    client: TestClient, make_account
) -> None:
    account = make_account(email="reviewer@vena-ia.dev")
    material = _create(
        client,
        account.headers,
        "MATERIAL",
        "TI-6AL4V",
        {"cutting_speed_m_min": 60, "feed_per_tooth_mm": 0.03},
    )
    machine = _create(
        client,
        account.headers,
        "MACHINE",
        "MILL-003",
        {"operations": ["milling"], "max_rpm": 10000, "max_feed_mm_min": 3000},
    )
    tool = _create(
        client,
        account.headers,
        "TOOL",
        "EM-6-4F",
        {"operations": ["milling"], "diameter_mm": 6, "teeth": 4},
    )
    payload = {
        "material_id": material["id"],
        "machine_id": machine["id"],
        "tool_id": tool["id"],
        "operation": "milling",
        "cutting_length_mm": 500,
    }
    first = client.post("/engineering/reports/preliminary", headers=account.headers, json=payload)
    second = client.post("/engineering/reports/preliminary", headers=account.headers, json=payload)
    assert first.status_code == second.status_code == 200
    left, right = first.json(), second.json()
    left.pop("generated_at")
    right.pop("generated_at")
    assert left == right
    assert left["schema_version"] == "vena-ia.engineering-review-report/v1"
    assert left["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert left["conclusion"] == "INSUFFICIENT_DATA"
    assert left["uncertainty"] in {
        "LOW_INFORMATION_CONFIDENCE",
        "MEDIUM_INFORMATION_CONFIDENCE",
        "HIGH_INFORMATION_CONFIDENCE",
    }
    assert all(item["status"] == "REQUIRED" for item in left["review_checklist"])
    assert "toolpath" in left["unavailable_items"]
    forbidden = {
        "APPROVED_FOR_PRODUCTION",
        "SAFE_TO_MACHINE",
        "CNC_READY",
        "RELEASED",
        "VALIDATED_FOR_MACHINE",
    }
    assert not forbidden.intersection(str(left))


def test_review_report_requires_authentication(client: TestClient) -> None:
    assert client.post("/engineering/reports/preliminary", json={}).status_code == 401


def test_catalog_isolated_by_organization_and_allows_same_version(
    client: TestClient, make_account
) -> None:
    first = make_account("catalog-org-a@vena-ia.dev")
    second = make_account("catalog-org-b@vena-ia.dev")
    first_item = _create(client, first.headers, "MATERIAL", "SHARED-CODE")
    second_item = _create(client, second.headers, "MATERIAL", "SHARED-CODE")
    first_org = _organization(client, first.headers)
    second_org = _organization(client, second.headers)

    assert first_item["organization_id"] == first_org
    assert second_item["organization_id"] == second_org
    assert first_item["scope_type"] == second_item["scope_type"] == "ORGANIZATION_OWNED"
    assert client.get(
        f"/engineering/catalogs?organization_id={second_org}", headers=first.headers
    ).status_code == 404
    denied = client.post(
        "/engineering/selections/preliminary",
        headers=first.headers,
        json={
            "material_id": second_item["id"],
            "machine_id": second_item["id"],
            "tool_id": second_item["id"],
            "operation": "MILLING",
        },
    )
    assert denied.status_code == 404


def test_catalog_version_is_unique_within_organization(
    client: TestClient, make_account
) -> None:
    account = make_account("catalog-unique@vena-ia.dev")
    _create(client, account.headers, "MATERIAL", "UNIQUE-IN-ORG")
    duplicate = client.post(
        f"/engineering/catalogs?organization_id={_organization(client, account.headers)}",
        headers=account.headers,
        json={
            "kind": "MATERIAL",
            "code": "UNIQUE-IN-ORG",
            "name": "Duplicate",
            "data_version": "2026.08",
            "source": "Concurrent duplicate fixture",
            "properties": {},
        },
    )
    assert duplicate.status_code == 409


def test_catalog_create_and_denial_reuse_security_audit(
    client: TestClient, make_account, db_session
) -> None:
    owner = make_account("catalog-audit-owner@vena-ia.dev")
    outsider = make_account("catalog-audit-outsider@vena-ia.dev")
    organization_id = _organization(client, owner.headers)
    _create(client, owner.headers, "TOOL", "AUDITED-CREATE")
    denied = client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=outsider.headers,
        json={
            "kind": "TOOL",
            "code": "AUDITED-DENIAL",
            "name": "Denied",
            "data_version": "2026.08",
            "source": "Audit fixture",
            "properties": {},
        },
    )
    assert denied.status_code == 404
    events = list(
        db_session.scalars(
            select(SecurityAuditEvent)
            .where(SecurityAuditEvent.event_type == "ENGINEERING_CATALOG_CREATED")
            .order_by(SecurityAuditEvent.occurred_at)
        )
    )
    assert [event.outcome for event in events[-2:]] == ["ALLOWED", "DENIED"]
    assert events[-2].actor_user_id == owner.id
    assert events[-1].actor_user_id == outsider.id


def test_member_reads_but_cannot_create_and_revocation_fails_closed(
    client: TestClient, make_account, db_session
) -> None:
    owner = make_account("catalog-owner@vena-ia.dev")
    member = make_account("catalog-member@vena-ia.dev")
    organization_id = _organization(client, owner.headers)
    item = _create(client, owner.headers, "MATERIAL", "MEMBER-VISIBLE")
    team = Team(organization_id=organization_id, name="Catalog readers")
    db_session.add(team)
    db_session.flush()
    membership = Membership(
        organization_id=organization_id,
        user_id=member.id,
        team_id=team.id,
        role="MEMBER",
        status="ACTIVE",
        created_by=owner.id,
    )
    db_session.add(membership)
    db_session.commit()

    listed = client.get(
        f"/engineering/catalogs?organization_id={organization_id}", headers=member.headers
    )
    assert listed.status_code == 200
    assert [entry["id"] for entry in listed.json()] == [item["id"]]
    create_denied = client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=member.headers,
        json={
            "kind": "TOOL",
            "code": "MEMBER-WRITE",
            "name": "Denied",
            "data_version": "2026.08",
            "source": "Denied fixture",
            "properties": {},
        },
    )
    assert create_denied.status_code == 404

    membership.status = "REVOKED"
    db_session.commit()
    assert client.get(
        f"/engineering/catalogs?organization_id={organization_id}", headers=member.headers
    ).status_code == 404


def test_scope_and_identity_cannot_be_mass_assigned(
    client: TestClient, make_account
) -> None:
    owner = make_account("catalog-mass-owner@vena-ia.dev")
    outsider = make_account("catalog-mass-outsider@vena-ia.dev")
    organization_id = _organization(client, owner.headers)
    forged_body = {
        "kind": "TOOL",
        "code": "FORGED-SCOPE",
        "name": "Forged",
        "data_version": "2026.08",
        "source": "Untrusted client",
        "properties": {},
        "scope_type": "SYSTEM_REFERENCE",
        "organization_id": organization_id,
        "created_by": owner.id,
    }
    assert client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=owner.headers,
        json=forged_body,
    ).status_code == 422
    assert client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers={**outsider.headers, "X-User-ID": owner.id, "X-Role": "OWNER"},
        json={key: value for key, value in forged_body.items() if key not in {
            "scope_type", "organization_id", "created_by"
        }},
    ).status_code == 404


def test_system_references_are_read_only_and_legacy_rows_are_hidden(
    client: TestClient, make_account, db_session
) -> None:
    account = make_account("catalog-reference@vena-ia.dev")
    system = EngineeringCatalogItem(
        kind="MATERIAL",
        code="SYSTEM-REFERENCE",
        name="System reference",
        data_version="2026.08",
        source="Controlled system fixture",
        properties={},
        scope_type="SYSTEM_REFERENCE",
        organization_id=None,
        created_by=account.id,
    )
    legacy = EngineeringCatalogItem(
        kind="MATERIAL",
        code="LEGACY-HIDDEN",
        name="Legacy hidden",
        data_version="2026.08",
        source="Pre-scope fixture",
        properties={},
        scope_type="LEGACY_UNSCOPED",
        organization_id=None,
        created_by=account.id,
    )
    db_session.add_all([system, legacy])
    db_session.commit()

    listed = client.get("/engineering/catalogs", headers=account.headers)
    assert listed.status_code == 200
    assert [entry["code"] for entry in listed.json()] == ["SYSTEM-REFERENCE"]
    assert listed.json()[0]["organization_id"] is None
    assert listed.json()[0]["scope_type"] == "SYSTEM_REFERENCE"
    assert "LEGACY-HIDDEN" not in str(listed.json())


def test_catalog_update_and_delete_are_not_exposed(client: TestClient, make_account) -> None:
    account = make_account("catalog-no-mutation@vena-ia.dev")
    item = _create(client, account.headers, "TOOL", "IMMUTABLE-CATALOG")
    assert client.patch(
        f"/engineering/catalogs/{item['id']}", headers=account.headers, json={"name": "Changed"}
    ).status_code == 404
    assert client.delete(
        f"/engineering/catalogs/{item['id']}", headers=account.headers
    ).status_code == 404


def test_catalog_openapi_is_additive_and_authority_fields_are_closed(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    create = schema["paths"]["/engineering/catalogs"]["post"]
    organization_parameter = next(
        parameter for parameter in create["parameters"] if parameter["name"] == "organization_id"
    )
    assert organization_parameter["in"] == "query"
    assert organization_parameter["required"] is True
    create_schema = schema["components"]["schemas"]["CatalogItemCreate"]
    assert create_schema["additionalProperties"] is False
    assert not {"organization_id", "scope_type", "created_by", "role"}.intersection(
        create_schema["properties"]
    )
    read_properties = schema["components"]["schemas"]["CatalogItemRead"]["properties"]
    assert {"scope_type", "organization_id"}.issubset(read_properties)
    assert "/engineering/catalogs/{catalog_id}" not in schema["paths"]
