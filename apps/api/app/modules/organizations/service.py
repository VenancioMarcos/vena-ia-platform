from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.modules.organizations.models import (
    Membership,
    Organization,
    PilotContext,
    PilotReadinessChecklist,
    Team,
)
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.schemas import (
    MembershipCreate,
    OrganizationCreate,
    OrganizationRole,
    OrganizationUpdate,
    PilotContextCreate,
    PilotStatus,
    ReadinessChecklistUpdate,
    TeamCreate,
    TeamUpdate,
)
from app.modules.users.models import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OrganizationAuthorization:
    """Fail-closed organization/team authorization derived only from database membership."""

    def __init__(self, repository: OrganizationRepository, user: User) -> None:
        self.repository = repository
        self.user = user

    def memberships(self, organization_id: str) -> list[Membership]:
        memberships = self.repository.active_memberships(organization_id, self.user.id)
        if not memberships:
            raise HTTPException(status_code=404, detail="Organization not found")
        return memberships

    def require_organization(self, organization_id: str) -> Organization:
        organization = self.repository.get_organization(organization_id)
        if organization is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        self.memberships(organization_id)
        return organization

    def require_role(
        self, organization_id: str, allowed: set[OrganizationRole]
    ) -> tuple[Organization, Membership]:
        organization = self.repository.get_organization(organization_id)
        memberships = (
            self.repository.active_memberships(organization_id, self.user.id)
            if organization is not None
            else []
        )
        membership = next(
            (
                item
                for item in memberships
                if item.team_id is None and OrganizationRole(item.role) in allowed
            ),
            None,
        )
        if organization is None or membership is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        return organization, membership

    def require_team(self, organization_id: str, team_id: str) -> Team:
        team = self.repository.get_team(team_id)
        if team is None or team.organization_id != organization_id:
            raise HTTPException(status_code=404, detail="Team not found")
        memberships = self.memberships(organization_id)
        allowed = any(
            (item.team_id is None and item.role in {"OWNER", "ADMIN"})
            or (item.team_id == team_id and item.role == "MEMBER")
            for item in memberships
        )
        if not allowed:
            raise HTTPException(status_code=404, detail="Team not found")
        return team


class OrganizationService:
    """Transactional service contract for controlled local onboarding."""

    def __init__(self, repository: OrganizationRepository, user: User) -> None:
        self.repository = repository
        self.user = user
        self.authorization = OrganizationAuthorization(repository, user)

    def _commit(self, instance: object) -> None:
        try:
            self.repository.commit()
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise HTTPException(status_code=409, detail="Resource already exists") from exc
        self.repository.refresh(instance)

    def create_organization(self, payload: OrganizationCreate) -> Organization:
        organization = Organization(name=payload.name)
        self.repository.add(organization)
        self.repository.db.flush()
        owner = Membership(
            organization_id=organization.id,
            user_id=self.user.id,
            team_id=None,
            role="OWNER",
            created_by=self.user.id,
        )
        self.repository.add(owner)
        self._commit(organization)
        return organization

    def update_organization(
        self, organization_id: str, payload: OrganizationUpdate
    ) -> Organization:
        organization, _ = self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        for name, value in payload.model_dump(exclude_none=True, mode="json").items():
            setattr(organization, name, value)
        organization.updated_at = _utcnow()
        self._commit(organization)
        return organization

    def create_team(self, organization_id: str, payload: TeamCreate) -> Team:
        self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        team = Team(organization_id=organization_id, name=payload.name)
        self.repository.add(team)
        self._commit(team)
        return team

    def update_team(self, organization_id: str, team_id: str, payload: TeamUpdate) -> Team:
        self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        team = self.repository.get_team(team_id)
        if team is None or team.organization_id != organization_id:
            raise HTTPException(status_code=404, detail="Team not found")
        for name, value in payload.model_dump(exclude_none=True, mode="json").items():
            setattr(team, name, value)
        team.updated_at = _utcnow()
        self._commit(team)
        return team

    def create_membership(
        self, organization_id: str, payload: MembershipCreate
    ) -> Membership:
        _, actor = self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        if payload.role == OrganizationRole.OWNER:
            raise HTTPException(status_code=422, detail="Ownership transfer is not supported")
        if actor.role == "ADMIN" and payload.role != OrganizationRole.MEMBER:
            raise HTTPException(status_code=403, detail="Role assignment denied")
        if self.repository.db.get(User, payload.user_id) is None:
            raise HTTPException(status_code=404, detail="User not found")
        if payload.team_id is not None:
            team = self.repository.get_team(payload.team_id)
            if team is None or team.organization_id != organization_id:
                raise HTTPException(status_code=404, detail="Team not found")
        existing = self.repository.find_membership(
            organization_id, payload.user_id, payload.team_id
        )
        if existing is not None:
            raise HTTPException(status_code=409, detail="Membership already exists")
        membership = Membership(
            organization_id=organization_id,
            user_id=payload.user_id,
            team_id=payload.team_id,
            role=payload.role.value,
            created_by=self.user.id,
        )
        self.repository.add(membership)
        self._commit(membership)
        return membership

    def change_role(
        self, organization_id: str, membership_id: str, role: OrganizationRole
    ) -> Membership:
        self.authorization.require_role(organization_id, {OrganizationRole.OWNER})
        membership = self.repository.get_membership(membership_id)
        if membership is None or membership.organization_id != organization_id:
            raise HTTPException(status_code=404, detail="Membership not found")
        if membership.role == "OWNER" or role == OrganizationRole.OWNER:
            raise HTTPException(status_code=422, detail="Ownership transfer is not supported")
        if role == OrganizationRole.MEMBER and membership.team_id is None:
            raise HTTPException(status_code=422, detail="MEMBER requires a team scope")
        if role == OrganizationRole.ADMIN and membership.team_id is not None:
            existing = self.repository.find_membership(
                organization_id, membership.user_id, None
            )
            if existing is not None and existing.id != membership.id:
                raise HTTPException(status_code=409, detail="Membership already exists")
            membership.team_id = None
        membership.role = role.value
        membership.updated_at = _utcnow()
        self._commit(membership)
        return membership

    def revoke_membership(self, organization_id: str, membership_id: str) -> Membership:
        _, actor = self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        membership = self.repository.get_membership(membership_id)
        if membership is None or membership.organization_id != organization_id:
            raise HTTPException(status_code=404, detail="Membership not found")
        if membership.role == "OWNER":
            raise HTTPException(status_code=422, detail="Organization owner cannot be revoked")
        if actor.role == "ADMIN" and membership.role != "MEMBER":
            raise HTTPException(status_code=403, detail="Membership revocation denied")
        membership.status = "REVOKED"
        membership.revoked_at = _utcnow()
        membership.updated_at = membership.revoked_at
        self._commit(membership)
        return membership

    def create_pilot_context(self, payload: PilotContextCreate) -> PilotContext:
        self.authorization.require_organization(payload.organization_id)
        if payload.team_id is not None:
            self.authorization.require_team(payload.organization_id, payload.team_id)
        context = PilotContext(
            organization_id=payload.organization_id,
            team_id=payload.team_id,
            name=payload.name,
            scope=payload.scope,
            owner_user_id=self.user.id,
        )
        self.repository.add(context)
        self._commit(context)
        return context

    def require_pilot_context(self, context_id: str) -> PilotContext:
        context = self.repository.get_pilot_context(context_id)
        if context is None:
            raise HTTPException(status_code=404, detail="Pilot context not found")
        self.authorization.require_organization(context.organization_id)
        if context.team_id is not None:
            self.authorization.require_team(context.organization_id, context.team_id)
        return context

    def transition_pilot_context(
        self, context_id: str, target: PilotStatus
    ) -> PilotContext:
        context = self.require_pilot_context(context_id)
        transitions = {
            "DRAFT": {"READINESS_IN_PROGRESS", "CLOSED"},
            "READINESS_IN_PROGRESS": {"READY_FOR_SYNTHETIC_REHEARSAL", "CLOSED"},
            "READY_FOR_SYNTHETIC_REHEARSAL": {"CLOSED"},
            "CLOSED": set(),
        }
        if target.value not in transitions[context.status]:
            raise HTTPException(status_code=409, detail="Invalid pilot context transition")
        if target == PilotStatus.READY_FOR_SYNTHETIC_REHEARSAL:
            checklist = self.repository.get_checklist(context.id)
            if checklist is None or checklist.result != "READY_FOR_HUMAN_REVIEW":
                raise HTTPException(status_code=409, detail="Readiness checklist is incomplete")
        context.status = target.value
        context.updated_at = _utcnow()
        self._commit(context)
        return context

    def update_checklist(
        self, context_id: str, payload: ReadinessChecklistUpdate
    ) -> PilotReadinessChecklist:
        context = self.require_pilot_context(context_id)
        if context.status == "CLOSED":
            raise HTTPException(status_code=409, detail="Pilot context is closed")
        categories = {item.category for item in payload.items}
        required = {
            "identity",
            "authorization",
            "recovery",
            "observability",
            "capacity",
            "privacy",
            "incident",
            "engineering_safety",
            "cnc_safety",
        }
        items_ready = categories == required and all(
            item.status.value in {"SATISFIED_BY_EVIDENCE", "NOT_APPLICABLE"}
            and (item.status.value != "SATISFIED_BY_EVIDENCE" or item.evidence_reference)
            for item in payload.items
        )
        privacy = payload.privacy.model_dump()
        result = "READY_FOR_HUMAN_REVIEW" if items_ready and all(privacy.values()) else "INCOMPLETE"
        checklist = self.repository.get_checklist(context_id)
        if checklist is None:
            checklist = PilotReadinessChecklist(
                pilot_context_id=context_id,
                items=[item.model_dump(mode="json") for item in payload.items],
                privacy=privacy,
                result=result,
                updated_by=self.user.id,
            )
            self.repository.add(checklist)
        else:
            checklist.items = [item.model_dump(mode="json") for item in payload.items]
            checklist.privacy = privacy
            checklist.result = result
            checklist.updated_by = self.user.id
            checklist.updated_at = _utcnow()
        if context.status == "DRAFT":
            context.status = "READINESS_IN_PROGRESS"
            context.updated_at = _utcnow()
        self._commit(checklist)
        return checklist
