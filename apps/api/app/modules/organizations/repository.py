from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organizations.models import (
    Membership,
    Organization,
    PilotContext,
    PilotReadinessChecklist,
    Team,
)


class OrganizationRepository:
    """Persistence contract for the organizational boundary."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_organization(self, organization_id: str) -> Organization | None:
        return self.db.get(Organization, organization_id)

    def get_team(self, team_id: str) -> Team | None:
        return self.db.get(Team, team_id)

    def get_membership(self, membership_id: str) -> Membership | None:
        return self.db.get(Membership, membership_id)

    def active_memberships(self, organization_id: str, user_id: str) -> list[Membership]:
        stmt = select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user_id,
            Membership.status == "ACTIVE",
        )
        return list(self.db.scalars(stmt))

    def list_memberships(self, organization_id: str) -> list[Membership]:
        stmt = select(Membership).where(Membership.organization_id == organization_id).order_by(
            Membership.created_at
        )
        return list(self.db.scalars(stmt))

    def find_membership(
        self, organization_id: str, user_id: str, team_id: str | None
    ) -> Membership | None:
        stmt = select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user_id,
            Membership.team_id.is_(None)
            if team_id is None
            else Membership.team_id == team_id,
        )
        return self.db.scalar(stmt)

    def list_organizations_for(self, user_id: str) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user_id, Membership.status == "ACTIVE")
            .distinct()
            .order_by(Organization.created_at)
        )
        return list(self.db.scalars(stmt))

    def list_teams(self, organization_id: str) -> list[Team]:
        return list(
            self.db.scalars(
                select(Team)
                .where(Team.organization_id == organization_id)
                .order_by(Team.created_at)
            )
        )

    def get_pilot_context(self, context_id: str) -> PilotContext | None:
        return self.db.get(PilotContext, context_id)

    def get_checklist(self, context_id: str) -> PilotReadinessChecklist | None:
        return self.db.scalar(
            select(PilotReadinessChecklist).where(
                PilotReadinessChecklist.pilot_context_id == context_id
            )
        )

    def add(self, instance: object) -> None:
        self.db.add(instance)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
