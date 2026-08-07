from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrganizationRole(StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class ResourceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class MembershipStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class PilotStatus(StrEnum):
    DRAFT = "DRAFT"
    READINESS_IN_PROGRESS = "READINESS_IN_PROGRESS"
    READY_FOR_SYNTHETIC_REHEARSAL = "READY_FOR_SYNTHETIC_REHEARSAL"
    CLOSED = "CLOSED"


class ChecklistItemStatus(StrEnum):
    REQUIRED = "REQUIRED"
    SATISFIED_BY_EVIDENCE = "SATISFIED_BY_EVIDENCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class OrganizationCreate(StrictModel):
    name: str = Field(min_length=1, max_length=255)


class OrganizationUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    status: ResourceStatus | None = None


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.organization/v1"
    id: str
    name: str
    status: ResourceStatus
    created_at: datetime
    updated_at: datetime


class TeamCreate(StrictModel):
    name: str = Field(min_length=1, max_length=255)


class TeamUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    status: ResourceStatus | None = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.team/v1"
    id: str
    organization_id: str
    name: str
    status: ResourceStatus
    created_at: datetime
    updated_at: datetime


class MembershipCreate(StrictModel):
    user_id: str
    team_id: str | None = None
    role: OrganizationRole

    @model_validator(mode="after")
    def validate_scope(self) -> "MembershipCreate":
        if self.role == OrganizationRole.MEMBER and self.team_id is None:
            raise ValueError("MEMBER requires a team_id")
        if self.role != OrganizationRole.MEMBER and self.team_id is not None:
            raise ValueError("OWNER and ADMIN memberships are organization scoped")
        return self


class MembershipRoleUpdate(StrictModel):
    role: OrganizationRole


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.membership/v1"
    id: str
    organization_id: str
    user_id: str
    team_id: str | None
    role: OrganizationRole
    status: MembershipStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None


class PilotContextCreate(StrictModel):
    organization_id: str
    team_id: str | None = None
    name: str = Field(min_length=1, max_length=255)
    scope: str = Field(min_length=1, max_length=1000)


class PilotContextTransition(StrictModel):
    status: PilotStatus


class PilotContextRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.pilot-context/v1"
    id: str
    organization_id: str
    team_id: str | None
    name: str
    status: PilotStatus
    owner_user_id: str
    scope: str
    review_status: str
    created_at: datetime
    updated_at: datetime
    limitations: list[str] = [
        "READY_FOR_SYNTHETIC_REHEARSAL does not authorize a real pilot or deploy.",
        "No CNC, production, customer, or commercial approval is represented.",
    ]


class ChecklistItem(StrictModel):
    category: str = Field(pattern=r"^(identity|authorization|recovery|observability|capacity|privacy|incident|engineering_safety|cnc_safety)$")
    status: ChecklistItemStatus
    evidence_reference: str | None = Field(default=None, max_length=500)


class PrivacyChecklist(StrictModel):
    synthetic_data_only: bool
    no_customer_data: bool
    no_credentials_in_evidence: bool
    retention_reviewed: bool
    deletion_path_defined: bool
    logs_redacted: bool
    access_scope_reviewed: bool


class ReadinessChecklistUpdate(StrictModel):
    items: list[ChecklistItem] = Field(min_length=1, max_length=50)
    privacy: PrivacyChecklist


class ReadinessChecklistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str = "vena-ia.pilot-readiness-checklist/v1"
    id: str
    pilot_context_id: str
    items: list[ChecklistItem]
    privacy: PrivacyChecklist
    result: str
    updated_by: str
    updated_at: datetime
    human_review_required: bool = True
