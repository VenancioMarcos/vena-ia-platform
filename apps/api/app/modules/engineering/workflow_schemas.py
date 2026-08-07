from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.modules.cad.schemas import GeometryAnalysisContract, GeometryFeaturesContract
from app.modules.cnc.schemas import CNCPlanPreview
from app.modules.engineering.schemas import (
    EngineeringRecommendation,
    EngineeringReviewReport,
    FeaturePlanningRequest,
    FeaturePlanningResponse,
)


class WorkflowStatus(StrEnum):
    COMPLETE_PRELIMINARY = "COMPLETE_PRELIMINARY"
    PARTIAL = "PARTIAL"
    BLOCKED_MISSING_INPUT = "BLOCKED_MISSING_INPUT"
    BLOCKED_UNSUPPORTED_FEATURE = "BLOCKED_UNSUPPORTED_FEATURE"
    FAILED = "FAILED"


class WorkflowReviewStatus(StrEnum):
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class IntegratedWorkflowRequest(FeaturePlanningRequest):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    tool_number: int | None = Field(default=None, ge=1, le=999)
    clearance_z_mm: float | None = Field(default=None, gt=0, le=1_000)


class SourceDocumentReference(BaseModel):
    document_id: str
    filename: str
    source_format: str = "STEP_PART_21"


class IntegratedEngineeringReport(BaseModel):
    schema_version: str = "vena-ia.integrated-engineering-report/v1"
    status: WorkflowReviewStatus = WorkflowReviewStatus.REQUIRES_HUMAN_REVIEW
    source_document_reference: str
    geometry_reference: str
    feature_reference: str
    planning_reference: str | None
    cnc_neutral_plan_reference: str | None
    engineering_review: EngineeringReviewReport | None
    assumptions: list[str]
    missing_inputs: list[str]
    limitations: list[str]
    human_review_checklist: list[str]
    conclusion: WorkflowStatus


class IntegratedEngineeringWorkflow(BaseModel):
    schema_version: str = "vena-ia.integrated-engineering-workflow/v1"
    workflow_id: str
    source_document: SourceDocumentReference
    geometry: GeometryAnalysisContract
    features: GeometryFeaturesContract
    engineering: EngineeringRecommendation | None
    planning: FeaturePlanningResponse | None
    cnc_neutral_plan: CNCPlanPreview | None
    integrated_report: IntegratedEngineeringReport
    assumptions: list[str]
    missing_inputs: list[str]
    limitations: list[str]
    warnings: list[str]
    traceability: list[str]
    review_status: WorkflowReviewStatus = WorkflowReviewStatus.REQUIRES_HUMAN_REVIEW
    workflow_status: WorkflowStatus
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
