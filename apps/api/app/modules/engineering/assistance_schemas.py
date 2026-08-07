from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.engineering.workflow_schemas import (
    IntegratedEngineeringWorkflow,
    IntegratedWorkflowRequest,
    WorkflowStatus,
)


class AssistanceProfile(StrEnum):
    CAD_ANALYSIS = "CAD_ANALYSIS"
    MANUFACTURING_ENGINEERING = "MANUFACTURING_ENGINEERING"
    RESEARCH = "RESEARCH"
    DOCUMENTATION_REPORTING = "DOCUMENTATION_REPORTING"


class AssistanceStatus(StrEnum):
    AVAILABLE_FOR_REVIEW = "AVAILABLE_FOR_REVIEW"
    PARTIAL = "PARTIAL"
    BLOCKED_MISSING_EVIDENCE = "BLOCKED_MISSING_EVIDENCE"
    BLOCKED_UNAUTHORIZED_SOURCE = "BLOCKED_UNAUTHORIZED_SOURCE"
    FAILED = "FAILED"


class SpecializedAssistanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    profile: AssistanceProfile
    question: str = Field(min_length=3, max_length=4_000)
    workflow: IntegratedWorkflowRequest
    research_project_id: str | None = Field(default=None, min_length=36, max_length=36)
    doe_study_id: str | None = Field(default=None, min_length=1, max_length=36)
    anova_dataset_id: str | None = Field(default=None, min_length=1, max_length=36)
    research_report_id: str | None = Field(default=None, min_length=1, max_length=36)
    limit: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def validate_research_scope(self) -> "SpecializedAssistanceRequest":
        research_ids = (self.doe_study_id, self.anova_dataset_id, self.research_report_id)
        if self.profile is AssistanceProfile.RESEARCH and self.research_project_id is None:
            raise ValueError("RESEARCH profile requires research_project_id")
        if self.profile is not AssistanceProfile.RESEARCH and any(research_ids):
            raise ValueError("Research entity references require RESEARCH profile")
        return self


class GroundedCitation(BaseModel):
    document_id: str
    page_number: int | None
    chunk_id: str | None
    evidence_reference: str
    retrieval_method: str
    source_quality: str
    limitations: list[str]


class GroundedResearchContext(BaseModel):
    schema_version: str = "vena-ia.grounded-research-assistance/v1"
    project_id: str
    citations: list[GroundedCitation]
    excerpts: list[str]
    doe: dict[str, object] | None
    anova: dict[str, object] | None
    report: dict[str, object] | None
    method_limitations: list[str]
    missing_evidence: list[str]


class AssistanceGroundedContext(BaseModel):
    profile: AssistanceProfile
    workflow_status: WorkflowStatus
    workflow_facts: dict[str, object]
    research: GroundedResearchContext | None
    untrusted_content_present: bool = False


class SpecializedAssistanceResponse(BaseModel):
    schema_version: str = "vena-ia.specialized-assistance/v1"
    assistance_id: str
    profile: AssistanceProfile
    source_workflow_reference: str
    source_workflow: IntegratedEngineeringWorkflow
    evidence_references: list[str]
    grounded_context: AssistanceGroundedContext
    response: str | None
    provider: str | None
    model: str | None
    assumptions: list[str]
    limitations: list[str]
    warnings: list[str]
    missing_evidence: list[str]
    citations: list[GroundedCitation]
    review_status: Literal["REQUIRES_HUMAN_REVIEW"] = "REQUIRES_HUMAN_REVIEW"
    assistance_status: AssistanceStatus
    non_production: Literal[True] = True
    simulation_only: Literal[True] = True
    executable_output: Literal[False] = False
    deterministic_input_trace: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    traceability: list[str]
