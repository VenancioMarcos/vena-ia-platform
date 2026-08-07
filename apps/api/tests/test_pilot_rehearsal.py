from sqlalchemy import select

from app.modules.audit.models import SecurityAuditEvent
from app.modules.organizations.models import PilotContext, PilotReadinessChecklist
from app.modules.organizations.rehearsal import (
    AUTHORITATIVE_EVIDENCE,
    RehearsalRequest,
    RehearsalService,
)


def _readiness():
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
                "status": "SATISFIED_BY_EVIDENCE",
                "evidence_reference": f"synthetic:{category}",
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


def _plan():
    return {
        "source_plan_schema": "vena-ia.cnc-neutral-plan/v1",
        "status": "SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW",
        "executable_output": False,
        "controller_family": "FANUC_OI_STRATEGY_PLACEHOLDER",
        "machine_profile": "ROMI_D1250_PLANNED_COMPATIBILITY",
        "operation": "DRILLING",
        "parameters": {"tool_number": 1, "spindle_rpm": 1000, "feed_mm_min": 100},
        "validation_checks": ["POSITIVE_CLEARANCE", "HUMAN_REVIEW_REQUIRED"],
        "limitations": [
            "No toolpath or G-code is generated.",
            "Not approved for machine transmission or production.",
        ],
    }


def _ready_context(client, owner, *, team_id=None):
    organization = client.post(
        "/organizations", json={"name": "Synthetic Rehearsal Org"}, headers=owner.headers
    ).json()
    context = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "team_id": team_id,
            "name": "Synthetic Rehearsal",
            "scope": "bounded synthetic operational evidence",
        },
        headers=owner.headers,
    ).json()
    checklist = client.put(
        f"/pilot-contexts/{context['id']}/readiness",
        json=_readiness(),
        headers=owner.headers,
    )
    assert checklist.status_code == 200, checklist.text
    transitioned = client.patch(
        f"/pilot-contexts/{context['id']}/status",
        json={"status": "READY_FOR_SYNTHETIC_REHEARSAL"},
        headers=owner.headers,
    )
    assert transitioned.status_code == 200, transitioned.text
    return organization, transitioned.json()


def _run(client, owner, context_id, key="synthetic-package2-rehearsal"):
    return client.post(
        f"/pilot-contexts/{context_id}/rehearsals",
        json={"rehearsal_key": key, "neutral_cnc_plan": _plan()},
        headers=owner.headers,
    )


def test_rehearsal_requires_ready_context(client, make_account):
    owner = make_account("rehearsal-state@vena-ia.dev")
    organization = client.post(
        "/organizations", json={"name": "State Gate Org"}, headers=owner.headers
    ).json()
    context = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "name": "Not ready",
            "scope": "synthetic",
        },
        headers=owner.headers,
    ).json()
    assert _run(client, owner, context["id"]).status_code == 409


def test_rehearsal_builds_review_only_integrity_bundle(client, make_account):
    owner = make_account("rehearsal-success@vena-ia.dev")
    organization, context = _ready_context(client, owner)
    response = _run(client, owner, context["id"])
    assert response.status_code == 200, response.text
    bundle = response.json()
    assert bundle["schema_version"] == "vena-ia.pilot-evidence/v1"
    assert bundle["organization_id"] == organization["id"]
    assert bundle["readiness_status"] == "READY_FOR_HUMAN_REVIEW"
    assert bundle["review_status"] == "REQUIRES_HUMAN_REVIEW"
    assert bundle["rollback_status"] == "DEFINED_NOT_EXECUTED"
    assert len(bundle["integrity_sha256"]) == 64
    assert bundle["integrity_semantics"].endswith("not an authenticity signature.")
    categories = {item["category"] for item in bundle["evidence_items"]}
    assert {"restore", "incident", "privacy", "cnc_virtual_validation"}.issubset(categories)
    assert bundle["slo_proposals"][0]["environment"] == "SYNTHETIC_NON_PRODUCTION"
    assert bundle["capacity_acceptance"]["environment"] == "SYNTHETIC_NON_PRODUCTION"


def test_rehearsal_replay_is_deterministic(client, make_account):
    owner = make_account("rehearsal-replay@vena-ia.dev")
    _, context = _ready_context(client, owner)
    first = _run(client, owner, context["id"]).json()
    second = _run(client, owner, context["id"]).json()
    assert first == second


def test_member_cannot_start_rehearsal(client, make_account):
    owner = make_account("rehearsal-owner@vena-ia.dev")
    member = make_account("rehearsal-member@vena-ia.dev")
    organization = client.post(
        "/organizations", json={"name": "Role Gate Org"}, headers=owner.headers
    ).json()
    team = client.post(
        f"/organizations/{organization['id']}/teams",
        json={"name": "Synthetic Team"},
        headers=owner.headers,
    ).json()
    client.post(
        f"/organizations/{organization['id']}/memberships",
        json={"user_id": member.id, "role": "MEMBER", "team_id": team["id"]},
        headers=owner.headers,
    )
    context = client.post(
        "/pilot-contexts",
        json={
            "organization_id": organization["id"],
            "team_id": team["id"],
            "name": "Member denied",
            "scope": "synthetic",
        },
        headers=owner.headers,
    ).json()
    assert _run(client, member, context["id"]).status_code == 404


def test_cross_org_rehearsal_is_hidden(client, make_account):
    owner = make_account("rehearsal-cross-a@vena-ia.dev")
    outsider = make_account("rehearsal-cross-b@vena-ia.dev")
    _, context = _ready_context(client, owner)
    assert _run(client, outsider, context["id"]).status_code == 404


def test_virtual_cnc_validation_is_strictly_non_executable(client, make_account):
    owner = make_account("virtual-cnc@vena-ia.dev")
    _, context = _ready_context(client, owner)
    response = client.post(
        f"/pilot-contexts/{context['id']}/virtual-cnc-validation",
        json=_plan(),
        headers=owner.headers,
    )
    assert response.status_code == 200, response.text
    validation = response.json()
    assert validation["schema_version"] == "vena-ia.virtual-cnc-plan-validation/v1"
    assert validation["simulation_only"] is True
    assert validation["executable_output"] is False
    assert validation["human_review_required"] is True


def test_gcode_mcode_and_executable_payload_are_rejected(client, make_account):
    owner = make_account("virtual-cnc-negative@vena-ia.dev")
    _, context = _ready_context(client, owner)
    for dangerous in ("G01", "M03"):
        plan = _plan()
        plan["controller_family"] = dangerous
        response = client.post(
            f"/pilot-contexts/{context['id']}/virtual-cnc-validation",
            json=plan,
            headers=owner.headers,
        )
        assert response.status_code == 422
    plan = _plan()
    plan["executable_output"] = True
    assert (
        client.post(
            f"/pilot-contexts/{context['id']}/virtual-cnc-validation",
            json=plan,
            headers=owner.headers,
        ).status_code
        == 422
    )
    plan = _plan()
    plan["gcode"] = "G01 X10"
    assert (
        client.post(
            f"/pilot-contexts/{context['id']}/virtual-cnc-validation",
            json=plan,
            headers=owner.headers,
        ).status_code
        == 422
    )


def test_missing_restore_evidence_fails_closed(client, make_account, db_session):
    owner = make_account("rehearsal-missing@vena-ia.dev")
    _, context_data = _ready_context(client, owner)
    context = db_session.get(PilotContext, context_data["id"])
    checklist = db_session.scalar(
        select(PilotReadinessChecklist).where(
            PilotReadinessChecklist.pilot_context_id == context_data["id"]
        )
    )
    assert context is not None and checklist is not None
    request = RehearsalRequest(
        rehearsal_key="synthetic-missing-restore", neutral_cnc_plan=_plan()
    )
    sources = tuple(item for item in AUTHORITATIVE_EVIDENCE if item.category != "restore")
    try:
        RehearsalService(sources).build(context, checklist, request)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 409
        assert "restore" in str(getattr(exc, "detail", ""))
    else:
        raise AssertionError("Missing restore evidence must fail closed")


def test_privacy_failure_blocks_rehearsal(client, make_account, db_session):
    owner = make_account("rehearsal-privacy@vena-ia.dev")
    _, context_data = _ready_context(client, owner)
    checklist = db_session.scalar(
        select(PilotReadinessChecklist).where(
            PilotReadinessChecklist.pilot_context_id == context_data["id"]
        )
    )
    assert checklist is not None
    checklist.privacy = {**checklist.privacy, "logs_redacted": False}
    db_session.commit()
    assert _run(client, owner, context_data["id"]).status_code == 409


def test_rehearsal_uses_existing_audit_subsystem(client, make_account, db_session):
    owner = make_account("rehearsal-audit@vena-ia.dev")
    _, context = _ready_context(client, owner)
    assert _run(client, owner, context["id"]).status_code == 200
    events = set(db_session.scalars(select(SecurityAuditEvent.event_type)))
    assert {
        "PILOT_REHEARSAL_STARTED",
        "PILOT_EVIDENCE_GENERATED",
        "VIRTUAL_CNC_VALIDATION_COMPLETED",
        "PILOT_REHEARSAL_ROLLBACK_DEFINED",
        "PILOT_REHEARSAL_COMPLETED",
    }.issubset(events)
