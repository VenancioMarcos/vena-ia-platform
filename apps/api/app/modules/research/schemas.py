from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ScientificDocumentType(StrEnum):
    JOURNAL_ARTICLE = "JOURNAL_ARTICLE"
    CONFERENCE_PAPER = "CONFERENCE_PAPER"
    THESIS = "THESIS"
    DISSERTATION = "DISSERTATION"
    TECHNICAL_REPORT = "TECHNICAL_REPORT"
    BOOK_CHAPTER = "BOOK_CHAPTER"
    OTHER = "OTHER"


class MetadataSource(StrEnum):
    PDF_METADATA = "PDF_METADATA"
    TEXT_HEURISTIC = "TEXT_HEURISTIC"
    USER_PROVIDED = "USER_PROVIDED"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ArticleCreate(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    document_id: str = Field(min_length=36, max_length=36)
    title: str | None = Field(default=None, min_length=1, max_length=500)
    authors: list[str] = Field(default_factory=list, max_length=50)
    year: int | None = Field(default=None, ge=1000, le=2200)
    venue: str | None = Field(default=None, min_length=1, max_length=500)
    volume: str | None = Field(default=None, min_length=1, max_length=50)
    issue: str | None = Field(default=None, min_length=1, max_length=50)
    pages: str | None = Field(default=None, min_length=1, max_length=100)
    doi: str | None = Field(default=None, min_length=3, max_length=255)
    keywords: list[str] = Field(default_factory=list, max_length=50)
    abstract: str | None = Field(default=None, min_length=1, max_length=20_000)
    document_type: ScientificDocumentType = ScientificDocumentType.OTHER
    language: str | None = Field(default=None, min_length=2, max_length=20)
    metadata_source: MetadataSource = MetadataSource.USER_PROVIDED

    @model_validator(mode="after")
    def validate_lists(self) -> "ArticleCreate":
        if any(not value.strip() or len(value) > 255 for value in self.authors):
            raise ValueError("authors must contain non-empty values up to 255 characters")
        if any(not value.strip() or len(value) > 100 for value in self.keywords):
            raise ValueError("keywords must contain non-empty values up to 100 characters")
        return self


class ArticleUpdate(StrictModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    authors: list[str] | None = Field(default=None, max_length=50)
    year: int | None = Field(default=None, ge=1000, le=2200)
    venue: str | None = Field(default=None, min_length=1, max_length=500)
    volume: str | None = Field(default=None, min_length=1, max_length=50)
    issue: str | None = Field(default=None, min_length=1, max_length=50)
    pages: str | None = Field(default=None, min_length=1, max_length=100)
    doi: str | None = Field(default=None, min_length=3, max_length=255)
    keywords: list[str] | None = Field(default=None, max_length=50)
    abstract: str | None = Field(default=None, min_length=1, max_length=20_000)
    document_type: ScientificDocumentType | None = None
    language: str | None = Field(default=None, min_length=2, max_length=20)


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    document_id: str
    created_by: str
    title: str | None
    authors: list[str]
    year: int | None
    venue: str | None
    volume: str | None
    issue: str | None
    pages: str | None
    doi: str | None
    keywords: list[str]
    abstract: str | None
    document_type: str
    language: str | None
    metadata_status: str
    metadata_source: str
    created_at: datetime
    updated_at: datetime


class ReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    article_id: str
    raw_text: str
    authors: str | None
    title: str | None
    year: int | None
    venue: str | None
    doi: str | None
    page_number: int
    extraction_method: str
    status: str
    created_at: datetime


class ReferencesResponse(StrictModel):
    article_id: str
    status: str
    references: list[ReferenceRead]


class SynthesisRequest(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    question: str = Field(min_length=3, max_length=4_000)
    limit: int = Field(default=5, ge=1, le=20)


class EvidenceRead(StrictModel):
    document_id: str = Field(min_length=1, max_length=36)
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    score: float = Field(ge=0, le=1)
    excerpt: str = Field(min_length=1, max_length=1_000)


class SynthesisResponse(StrictModel):
    project_id: str
    question: str
    synthesis: str
    provider: str
    model: str
    evidence: list[EvidenceRead]
    status: str
    limitations: list[str]


class FactorType(StrEnum):
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"


class DOEDesignType(StrEnum):
    FULL_FACTORIAL = "FULL_FACTORIAL"
    TWO_LEVEL_FACTORIAL = "TWO_LEVEL_FACTORIAL"
    ONE_FACTOR_AT_A_TIME = "ONE_FACTOR_AT_A_TIME"
    CUSTOM_PRELIMINARY = "CUSTOM_PRELIMINARY"


class FactorInput(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    factor_type: FactorType
    minimum: float | None = None
    maximum: float | None = None
    categorical_levels: list[str] = Field(default_factory=list, max_length=20)
    notes: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def validate_levels(self) -> "FactorInput":
        if self.factor_type is FactorType.NUMERIC:
            if self.minimum is None or self.maximum is None or self.minimum >= self.maximum:
                raise ValueError("numeric factors require minimum < maximum")
            if self.categorical_levels:
                raise ValueError("numeric factors cannot have categorical levels")
        elif len(self.categorical_levels) < 2:
            raise ValueError("categorical factors require at least two levels")
        if len(set(self.categorical_levels)) != len(self.categorical_levels):
            raise ValueError("categorical levels must be unique")
        return self


class ResponseVariableInput(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    objective: str = Field(min_length=1, max_length=500)
    best_criterion: str | None = Field(default=None, max_length=100)


class DOEStudyCreate(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    name: str = Field(min_length=1, max_length=255)
    objective: str = Field(min_length=1, max_length=2_000)
    response_variables: list[ResponseVariableInput] = Field(min_length=1, max_length=20)
    factors: list[FactorInput] = Field(min_length=1, max_length=10)
    design_type: DOEDesignType
    repetitions: int = Field(default=1, ge=1, le=100)
    randomization_required: bool = True
    blocking_notes: str | None = Field(default=None, max_length=2_000)
    assumptions: list[str] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def unique_factor_names(self) -> "DOEStudyCreate":
        names = [factor.name.casefold() for factor in self.factors]
        if len(names) != len(set(names)):
            raise ValueError("factor names must be unique")
        return self


class DOEStudyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_by: str
    name: str
    objective: str
    response_variables: list[dict[str, object]]
    factors: list[dict[str, object]]
    design_type: str
    repetitions: int
    randomization_required: bool
    blocking_notes: str | None
    assumptions: list[str]
    status: str
    created_at: datetime
    updated_at: datetime


class ObservationInput(StrictModel):
    group: str = Field(min_length=1, max_length=100)
    value: float = Field(ge=-1e12, le=1e12)


class ANOVADatasetCreate(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    name: str = Field(min_length=1, max_length=255)
    factor_name: str = Field(min_length=1, max_length=255)
    response_name: str = Field(min_length=1, max_length=255)
    response_unit: str = Field(min_length=1, max_length=100)
    observations: list[ObservationInput] = Field(min_length=2, max_length=10_000)


class ANOVADatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_by: str
    name: str
    factor_name: str
    response_name: str
    response_unit: str
    observations: list[dict[str, object]]
    descriptive_summary: dict[str, object]
    assumptions_checklist: list[str]
    status: str
    created_at: datetime


class ReportType(StrEnum):
    TECHNICAL_SYNTHESIS = "TECHNICAL_SYNTHESIS"
    LITERATURE_REVIEW_PRELIMINARY = "LITERATURE_REVIEW_PRELIMINARY"
    ARTICLE_COMPARISON = "ARTICLE_COMPARISON"
    DOE_PLAN = "DOE_PLAN"
    ANOVA_DATA_PREPARATION = "ANOVA_DATA_PREPARATION"
    RESEARCH_PROJECT_BRIEF = "RESEARCH_PROJECT_BRIEF"


class ReportCreate(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    report_type: ReportType
    title: str = Field(min_length=1, max_length=500)
    objective: str = Field(min_length=1, max_length=2_000)
    document_ids: list[str] = Field(default_factory=list, max_length=50)
    synthesis: str = Field(min_length=1, max_length=100_000)
    evidence: list[EvidenceRead] = Field(default_factory=list, max_length=100)
    limitations: list[str] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_evidence_documents(self) -> "ReportCreate":
        known_documents = set(self.document_ids)
        if any(item.document_id not in known_documents for item in self.evidence):
            raise ValueError("evidence must reference a document listed in document_ids")
        return self


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_by: str
    report_type: str
    title: str
    objective: str
    document_ids: list[str]
    synthesis: str
    evidence: list[dict[str, object]]
    limitations: list[str]
    status: str
    created_at: datetime
