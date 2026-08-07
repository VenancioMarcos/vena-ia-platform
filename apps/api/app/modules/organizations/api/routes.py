from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response

from app.modules.audit.service import record_security_event
from app.modules.organizations.dependencies import OrganizationServiceDependency
from app.modules.organizations.models import (
    Membership,
    Organization,
    PilotContext,
    PilotReadinessChecklist,
    Team,
)
from app.modules.organizations.schemas import (
    MembershipCreate,
    MembershipRead,
    MembershipRoleUpdate,
    OrganizationCreate,
    OrganizationRead,
    OrganizationRole,
    OrganizationUpdate,
    PilotContextCreate,
    PilotContextRead,
    PilotContextTransition,
    ReadinessChecklistRead,
    ReadinessChecklistUpdate,
    TeamCreate,
    TeamRead,
    TeamUpdate,
)
from app.modules.organizations.rehearsal import (
    NeutralCNCPlan,
    PilotEvidenceBundle,
    IntegrityVerification,
    RehearsalRequest,
    RehearsalService,
    RollbackActionResult,
    RollbackRequest,
    RollbackResult,
    RollbackResultStatus,
    VirtualCNCValidation,
    validate_virtual_cnc,
    verify_bundle_integrity,
)

router = APIRouter(tags=["controlled-pilot"])


def _audit(
    request: Request,
    service: OrganizationServiceDependency,
    event_type: str,
    *,
    target_user_id: str | None = None,
) -> None:
    record_security_event(
        service.repository.db,
        request,
        event_type,
        outcome="SUCCESS",
        actor_user_id=service.user.id,
        target_user_id=target_user_id,
    )


@router.post("/organizations", response_model=OrganizationRead, status_code=201)
def create_organization(
    payload: OrganizationCreate, request: Request, service: OrganizationServiceDependency
) -> Organization:
    organization = service.create_organization(payload)
    _audit(request, service, "ORGANIZATION_CREATED")
    return organization


@router.get("/organizations", response_model=list[OrganizationRead])
def list_organizations(service: OrganizationServiceDependency) -> list[Organization]:
    return service.repository.list_organizations_for(service.user.id)


@router.get("/organizations/{organization_id}", response_model=OrganizationRead)
def get_organization(
    organization_id: str, service: OrganizationServiceDependency
) -> Organization:
    return service.authorization.require_organization(organization_id)


@router.patch("/organizations/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    service: OrganizationServiceDependency,
) -> Organization:
    return service.update_organization(organization_id, payload)


@router.post("/organizations/{organization_id}/teams", response_model=TeamRead, status_code=201)
def create_team(
    organization_id: str,
    payload: TeamCreate,
    request: Request,
    service: OrganizationServiceDependency,
) -> Team:
    team = service.create_team(organization_id, payload)
    _audit(request, service, "TEAM_CREATED")
    return team


@router.get("/organizations/{organization_id}/teams", response_model=list[TeamRead])
def list_teams(
    organization_id: str, service: OrganizationServiceDependency
) -> list[Team]:
    memberships = service.authorization.memberships(organization_id)
    if any(item.team_id is None and item.role in {"OWNER", "ADMIN"} for item in memberships):
        return service.repository.list_teams(organization_id)
    allowed_team_ids = {item.team_id for item in memberships if item.team_id is not None}
    return [
        team
        for team in service.repository.list_teams(organization_id)
        if team.id in allowed_team_ids
    ]


@router.get("/organizations/{organization_id}/teams/{team_id}", response_model=TeamRead)
def get_team(
    organization_id: str, team_id: str, service: OrganizationServiceDependency
) -> Team:
    return service.authorization.require_team(organization_id, team_id)


@router.patch("/organizations/{organization_id}/teams/{team_id}", response_model=TeamRead)
def update_team(
    organization_id: str,
    team_id: str,
    payload: TeamUpdate,
    service: OrganizationServiceDependency,
) -> Team:
    return service.update_team(organization_id, team_id, payload)


@router.post(
    "/organizations/{organization_id}/memberships",
    response_model=MembershipRead,
    status_code=201,
)
def create_membership(
    organization_id: str,
    payload: MembershipCreate,
    request: Request,
    service: OrganizationServiceDependency,
) -> Membership:
    membership = service.create_membership(organization_id, payload)
    _audit(request, service, "MEMBERSHIP_CREATED", target_user_id=membership.user_id)
    return membership


@router.get(
    "/organizations/{organization_id}/memberships", response_model=list[MembershipRead]
)
def list_memberships(
    organization_id: str, service: OrganizationServiceDependency
) -> list[Membership]:
    service.authorization.require_role(
        organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
    )
    return service.repository.list_memberships(organization_id)


@router.patch(
    "/organizations/{organization_id}/memberships/{membership_id}/role",
    response_model=MembershipRead,
)
def change_membership_role(
    organization_id: str,
    membership_id: str,
    payload: MembershipRoleUpdate,
    request: Request,
    service: OrganizationServiceDependency,
) -> Membership:
    membership = service.change_role(organization_id, membership_id, payload.role)
    _audit(request, service, "MEMBERSHIP_ROLE_CHANGED", target_user_id=membership.user_id)
    return membership


@router.delete(
    "/organizations/{organization_id}/memberships/{membership_id}", status_code=204
)
def revoke_membership(
    organization_id: str,
    membership_id: str,
    request: Request,
    service: OrganizationServiceDependency,
) -> Response:
    membership = service.revoke_membership(organization_id, membership_id)
    _audit(request, service, "MEMBERSHIP_REVOKED", target_user_id=membership.user_id)
    return Response(status_code=204)


@router.post("/pilot-contexts", response_model=PilotContextRead, status_code=201)
def create_pilot_context(
    payload: PilotContextCreate,
    request: Request,
    service: OrganizationServiceDependency,
) -> PilotContext:
    context = service.create_pilot_context(payload)
    _audit(request, service, "PILOT_CONTEXT_CREATED")
    return context


@router.get("/pilot-contexts/{context_id}", response_model=PilotContextRead)
def get_pilot_context(
    context_id: str, service: OrganizationServiceDependency
) -> PilotContext:
    return service.require_pilot_context(context_id)


@router.patch("/pilot-contexts/{context_id}/status", response_model=PilotContextRead)
def transition_pilot_context(
    context_id: str,
    payload: PilotContextTransition,
    request: Request,
    service: OrganizationServiceDependency,
) -> PilotContext:
    context = service.transition_pilot_context(context_id, payload.status)
    _audit(request, service, "PILOT_CONTEXT_STATE_CHANGED")
    return context


@router.put(
    "/pilot-contexts/{context_id}/readiness", response_model=ReadinessChecklistRead
)
def update_readiness(
    context_id: str,
    payload: ReadinessChecklistUpdate,
    request: Request,
    service: OrganizationServiceDependency,
) -> PilotReadinessChecklist:
    checklist = service.update_checklist(context_id, payload)
    _audit(request, service, "PILOT_READINESS_UPDATED")
    return checklist


@router.get(
    "/pilot-contexts/{context_id}/readiness", response_model=ReadinessChecklistRead
)
def get_readiness(
    context_id: str, service: OrganizationServiceDependency
) -> PilotReadinessChecklist:
    service.require_pilot_context(context_id)
    checklist = service.repository.get_checklist(context_id)
    if checklist is None:
        raise HTTPException(status_code=404, detail="Readiness checklist not found")
    return checklist


@router.post(
    "/pilot-contexts/{context_id}/virtual-cnc-validation",
    response_model=VirtualCNCValidation,
)
def virtual_cnc_validation(
    context_id: str,
    payload: NeutralCNCPlan,
    request: Request,
    service: OrganizationServiceDependency,
) -> VirtualCNCValidation:
    context = service.require_pilot_context(context_id)
    service.authorization.require_role(
        context.organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
    )
    validation = validate_virtual_cnc(payload)
    _audit(request, service, "VIRTUAL_CNC_VALIDATION_COMPLETED")
    return validation


@router.post(
    "/pilot-contexts/{context_id}/rehearsals", response_model=PilotEvidenceBundle
)
def run_synthetic_rehearsal(
    context_id: str,
    payload: RehearsalRequest,
    request: Request,
    service: OrganizationServiceDependency,
) -> PilotEvidenceBundle:
    context = service.require_pilot_context(context_id)
    service.authorization.require_role(
        context.organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
    )
    _audit(request, service, "PILOT_REHEARSAL_STARTED")
    try:
        bundle = RehearsalService().build(
            context, service.repository.get_checklist(context_id), payload
        )
    except HTTPException:
        _audit(request, service, "PILOT_EVIDENCE_FAILED")
        raise
    _audit(request, service, "PILOT_EVIDENCE_GENERATED")
    _audit(request, service, "VIRTUAL_CNC_VALIDATION_COMPLETED")
    _audit(request, service, "PILOT_REHEARSAL_ROLLBACK_DEFINED")
    _audit(request, service, "PILOT_REHEARSAL_COMPLETED")
    return bundle


@router.post(
    "/pilot-contexts/{context_id}/evidence/verify", response_model=IntegrityVerification
)
def verify_pilot_evidence(
    context_id: str,
    payload: PilotEvidenceBundle,
    service: OrganizationServiceDependency,
) -> IntegrityVerification:
    context = service.require_pilot_context(context_id)
    service.authorization.require_role(
        context.organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
    )
    if payload.pilot_context_id != context.id or payload.organization_id != context.organization_id:
        raise HTTPException(status_code=404, detail="Pilot evidence not found")
    return verify_bundle_integrity(payload)


@router.post(
    "/pilot-contexts/{context_id}/rehearsals/rollback", response_model=RollbackResult
)
def rollback_synthetic_rehearsal(
    context_id: str,
    payload: RollbackRequest,
    request: Request,
    service: OrganizationServiceDependency,
) -> RollbackResult:
    context = service.require_pilot_context(context_id)
    service.authorization.require_role(
        context.organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
    )
    now = datetime.now(timezone.utc)
    actions: list[RollbackActionResult] = []
    if context.status == "CLOSED":
        close_result = RollbackResultStatus.NOT_APPLICABLE
        close_warnings = ["Pilot Context was already closed."]
    else:
        context.status = "CLOSED"
        context.updated_at = now
        service.repository.commit()
        close_result = RollbackResultStatus.SUCCESS
        close_warnings = []
    actions.append(
        RollbackActionResult(
            action="CLOSE_PILOT_CONTEXT",
            target=context.id,
            result=close_result,
            warnings=close_warnings,
            evidence_reference=f"pilot-context:{context.id}",
            timestamp=now,
            responsible_actor=service.user.id,
        )
    )
    if payload.membership_id is not None:
        try:
            membership = service.revoke_membership(
                context.organization_id, payload.membership_id
            )
            result = RollbackResultStatus.SUCCESS
            warnings: list[str] = []
            reference = f"membership:{membership.id}:REVOKED"
        except HTTPException as exc:
            result = RollbackResultStatus.FAILED
            warnings = [str(exc.detail)]
            reference = f"membership:{payload.membership_id}:FAILED"
        actions.append(
            RollbackActionResult(
                action="REVOKE_SYNTHETIC_MEMBERSHIP",
                target=payload.membership_id,
                result=result,
                warnings=warnings,
                evidence_reference=reference,
                timestamp=now,
                responsible_actor=service.user.id,
            )
        )
    actions.append(
        RollbackActionResult(
            action="CLEAN_DISPOSABLE_FIXTURES",
            target="ephemeral-evidence",
            result=RollbackResultStatus.NOT_APPLICABLE,
            warnings=["No persistent Package 2 fixture or artifact exists."],
            evidence_reference="in-memory:cleared-on-response",
            timestamp=now,
            responsible_actor=service.user.id,
        )
    )
    results = {item.result for item in actions}
    if RollbackResultStatus.FAILED in results:
        overall = (
            RollbackResultStatus.PARTIAL
            if RollbackResultStatus.SUCCESS in results
            else RollbackResultStatus.FAILED
        )
    elif RollbackResultStatus.SUCCESS in results:
        overall = RollbackResultStatus.SUCCESS
    else:
        overall = RollbackResultStatus.NOT_APPLICABLE
    _audit(
        request,
        service,
        "PILOT_REHEARSAL_ROLLBACK_COMPLETED"
        if overall == RollbackResultStatus.SUCCESS
        else "PILOT_REHEARSAL_ROLLBACK_PARTIAL_OR_FAILED",
    )
    return RollbackResult(overall_result=overall, actions=actions)
