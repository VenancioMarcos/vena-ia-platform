from sqlalchemy import select

from app.modules.audit.models import SecurityAuditEvent
from app.modules.organizations.contracts import SCHEMA_VERSIONS
from app.modules.organizations.models import Membership


def _organization(client, account, name="Synthetic Organization"):
    response = client.post("/organizations", json={"name": name}, headers=account.headers)
    assert response.status_code == 201, response.text
    return response.json()


def _team(client, account, organization_id, name="Synthetic Team"):
    response = client.post(
        f"/organizations/{organization_id}/teams",
        json={"name": name},
        headers=account.headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _membership(client, owner, organization_id, user_id, role, team_id=None):
    response = client.post(
        f"/organizations/{organization_id}/memberships",
        json={"user_id": user_id, "role": role, "team_id": team_id},
        headers=owner.headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _readiness_payload(status="SATISFIED_BY_EVIDENCE"):
    categories = [
        "identity",
        "authorization",
        "recovery",
        "observability",
        "capacity",
        "privacy",
        "incident",
        "engineering_safety",
        "cnc_safety",
    ]
    return {
        "items": [
            {
                "category": category,
                "status": status,
                "evidence_reference": f"synthetic-evidence:{category}",
            }
            for category in categories
        ],
        "privacy": {
            "synthetic_data_only": True,
            "no_customer_data": True,
            "no_credentials_in_evidence": True,
            "retention_reviewed": True,
            "deletion_path_defined": True,
            "logs_redacted": True,
            "access_scope_reviewed": True,
        },
    }


def test_authentication_and_mass_assignment_fail_closed(client, make_account):
    owner = make_account("owner@vena-ia.dev")
    assert client.post("/organizations", json={"name": "No token"}).status_code == 401
    assert (
        client.post(
            "/organizations",
            json={"name": "Forged", "status": "ACTIVE", "owner_user_id": "forged"},
            headers=owner.headers,
        ).status_code
        == 422
    )


def test_onboarding_bootstraps_exact_authenticated_owner(client, make_account, db_session):
    owner = make_account("bootstrap@vena-ia.dev")
    organization = _organization(client, owner)
    membership = db_session.scalar(
        select(Membership).where(Membership.organization_id == organization["id"])
    )
    assert membership is not None
    assert (membership.user_id, membership.role, membership.team_id, membership.status) == (
        owner.id,
        "OWNER",
        None,
        "ACTIVE",
    )
    assert organization["schema_version"] == "vena-ia.organization/v1"


def test_x_user_id_and_cross_organization_do_not_grant_access(client, make_account):
    owner_a = make_account("owner-a@vena-ia.dev")
    owner_b = make_account("owner-b@vena-ia.dev")
    organization_a = _organization(client, owner_a, "Organization A")
    organization_b = _organization(client, owner_b, "Organization B")
    forged_headers = {**owner_a.headers, "X-User-ID": owner_b.id, "X-Role": "OWNER"}
    assert (
        client.get(f"/organizations/{organization_b['id']}", headers=forged_headers).status_code
        == 404
    )
    visible = client.get("/organizations", headers=forged_headers).json()
    assert [item["id"] for item in visible] == [organization_a["id"]]


def test_team_scoped_member_is_denied_cross_team(client, make_account):
    owner = make_account("owner-team@vena-ia.dev")
    member = make_account("member-team@vena-ia.dev")
    organization = _organization(client, owner)
    team_a = _team(client, owner, organization["id"], "Team A")
    team_b = _team(client, owner, organization["id"], "Team B")
    _membership(client, owner, organization["id"], member.id, "MEMBER", team_a["id"])
    assert (
        client.get(
            f"/organizations/{organization['id']}/teams/{team_a['id']}",
            headers=member.headers,
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/organizations/{organization['id']}/teams/{team_b['id']}",
            headers=member.headers,
        ).status_code
        == 404
    )


def test_role_allowlist_and_assignment_invariants(client, make_account):
    owner = make_account("owner-role@vena-ia.dev")
    admin = make_account("admin-role@vena-ia.dev")
    member = make_account("member-role@vena-ia.dev")
    organization = _organization(client, owner)
    team = _team(client, owner, organization["id"])
    admin_membership = _membership(client, owner, organization["id"], admin.id, "ADMIN")
    member_membership = _membership(
        client, admin, organization["id"], member.id, "MEMBER", team["id"]
    )
    assert admin_membership["role"] == "ADMIN"
    assert member_membership["role"] == "MEMBER"
    assert (
        client.post(
            f"/organizations/{organization['id']}/memberships",
            json={"user_id": member.id, "role": "SUPERADMIN"},
            headers=owner.headers,
        ).status_code
        == 422
    )
    assert (
        client.patch(
            f"/organizations/{organization['id']}/memberships/{member_membership['id']}/role",
            json={"role": "ADMIN"},
            headers=member.headers,
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/organizations/{organization['id']}/memberships/{member_membership['id']}/role",
            json={"role": "OWNER"},
            headers=owner.headers,
        ).status_code
        == 422
    )
    promoted = client.patch(
        f"/organizations/{organization['id']}/memberships/{member_membership['id']}/role",
        json={"role": "ADMIN"},
        headers=owner.headers,
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["role"] == "ADMIN"
    assert promoted.json()["team_id"] is None


def test_duplicate_membership_is_conflict(client, make_account):
    owner = make_account("owner-duplicate@vena-ia.dev")
    member = make_account("member-duplicate@vena-ia.dev")
    organization = _organization(client, owner)
    team = _team(client, owner, organization["id"])
    _membership(client, owner, organization["id"], member.id, "MEMBER", team["id"])
    duplicate = client.post(
        f"/organizations/{organization['id']}/memberships",
        json={"user_id": member.id, "role": "MEMBER", "team_id": team["id"]},
        headers=owner.headers,
    )
    assert duplicate.status_code == 409


def test_revoked_membership_fails_immediately(client, make_account):
    owner = make_account("owner-revoke@vena-ia.dev")
    member = make_account("member-revoke@vena-ia.dev")
    organization = _organization(client, owner)
    team = _team(client, owner, organization["id"])
    membership = _membership(
        client, owner, organization["id"], member.id, "MEMBER", team["id"]
    )
    revoked = client.delete(
        f"/organizations/{organization['id']}/memberships/{membership['id']}",
        headers=owner.headers,
    )
    assert revoked.status_code == 204
    assert (
        client.get(
            f"/organizations/{organization['id']}/teams/{team['id']}",
            headers=member.headers,
        ).status_code
        == 404
    )


def test_owner_cannot_be_revoked_or_reassigned(client, make_account, db_session):
    owner = make_account("sole-owner@vena-ia.dev")
    organization = _organization(client, owner)
    membership = db_session.scalar(
        select(Membership).where(Membership.organization_id == organization["id"])
    )
    assert membership is not None
    assert (
        client.delete(
            f"/organizations/{organization['id']}/memberships/{membership.id}",
            headers=owner.headers,
        ).status_code
        == 422
    )
    assert (
        client.patch(
            f"/organizations/{organization['id']}/memberships/{membership.id}/role",
            json={"role": "ADMIN"},
            headers=owner.headers,
        ).status_code
        == 422
    )


def test_pilot_context_derives_owner_and_rejects_body_authority(client, make_account):
    owner = make_account("pilot-owner@vena-ia.dev")
    organization = _organization(client, owner)
    invalid = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "name": "Forged pilot",
            "scope": "synthetic only",
            "owner_user_id": "forged",
            "status": "READY_FOR_SYNTHETIC_REHEARSAL",
        },
        headers=owner.headers,
    )
    assert invalid.status_code == 422
    created = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "name": "Synthetic readiness",
            "scope": "synthetic data and local evidence only",
        },
        headers=owner.headers,
    )
    assert created.status_code == 201, created.text
    assert created.json()["owner_user_id"] == owner.id
    assert created.json()["status"] == "DRAFT"
    assert "does not authorize" in created.json()["limitations"][0]


def test_readiness_requires_complete_evidence_and_human_review(client, make_account):
    owner = make_account("readiness-owner@vena-ia.dev")
    organization = _organization(client, owner)
    context = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "name": "Synthetic readiness",
            "scope": "synthetic only",
        },
        headers=owner.headers,
    ).json()
    incomplete_payload = _readiness_payload()
    incomplete_payload["privacy"]["logs_redacted"] = False
    incomplete = client.put(
        f"/pilot-contexts/{context['id']}/readiness",
        json=incomplete_payload,
        headers=owner.headers,
    )
    assert incomplete.status_code == 200
    assert incomplete.json()["result"] == "INCOMPLETE"
    denied = client.patch(
        f"/pilot-contexts/{context['id']}/status",
        json={"status": "READY_FOR_SYNTHETIC_REHEARSAL"},
        headers=owner.headers,
    )
    assert denied.status_code == 409
    ready = client.put(
        f"/pilot-contexts/{context['id']}/readiness",
        json=_readiness_payload(),
        headers=owner.headers,
    )
    assert ready.status_code == 200, ready.text
    assert ready.json()["result"] == "READY_FOR_HUMAN_REVIEW"
    assert ready.json()["human_review_required"] is True
    transitioned = client.patch(
        f"/pilot-contexts/{context['id']}/status",
        json={"status": "READY_FOR_SYNTHETIC_REHEARSAL"},
        headers=owner.headers,
    )
    assert transitioned.status_code == 200, transitioned.text


def test_cross_org_pilot_context_is_hidden(client, make_account):
    owner_a = make_account("pilot-a@vena-ia.dev")
    owner_b = make_account("pilot-b@vena-ia.dev")
    organization = _organization(client, owner_a)
    context = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "name": "Hidden synthetic context",
            "scope": "synthetic only",
        },
        headers=owner_a.headers,
    ).json()
    assert (
        client.get(f"/pilot-contexts/{context['id']}", headers=owner_b.headers).status_code
        == 404
    )


def test_operations_emit_existing_audit_events(client, make_account, db_session):
    owner = make_account("audit-owner@vena-ia.dev")
    organization = _organization(client, owner)
    _team(client, owner, organization["id"])
    event_types = set(db_session.scalars(select(SecurityAuditEvent.event_type)))
    assert {"ORGANIZATION_CREATED", "TEAM_CREATED"}.issubset(event_types)


def test_contracts_and_openapi_are_closed(client):
    assert SCHEMA_VERSIONS == {
        "vena-ia.organization/v1",
        "vena-ia.team/v1",
        "vena-ia.membership/v1",
        "vena-ia.pilot-context/v1",
        "vena-ia.pilot-readiness-checklist/v1",
        "vena-ia.pilot-evidence/v1",
        "vena-ia.virtual-cnc-plan-validation/v1",
    }
    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == "1.9.0"
    assert "/organizations" in schema["paths"]
    membership = schema["components"]["schemas"]["MembershipCreate"]
    assert membership["additionalProperties"] is False
    assert set(schema["components"]["schemas"]["OrganizationRole"]["enum"]) == {
        "OWNER",
        "ADMIN",
        "MEMBER",
    }
