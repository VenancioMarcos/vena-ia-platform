from fastapi import APIRouter, Response, status

from app.modules.research.dependencies import (
    ResearchServiceDependency,
    ResearchSynthesisServiceDependency,
)
from app.modules.research.schemas import (
    ANOVADatasetCreate,
    ANOVADatasetRead,
    ArticleCreate,
    ArticleRead,
    ArticleUpdate,
    DOEStudyCreate,
    DOEStudyRead,
    ReferenceRead,
    ReferencesResponse,
    ReportCreate,
    ReportRead,
    SynthesisRequest,
    SynthesisResponse,
)

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/articles", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: ArticleCreate,
    service: ResearchServiceDependency,
) -> ArticleRead:
    return ArticleRead.model_validate(service.create_article(payload))


@router.get("/articles", response_model=list[ArticleRead])
def list_articles(
    project_id: str,
    service: ResearchServiceDependency,
) -> list[ArticleRead]:
    return [
        ArticleRead.model_validate(article)
        for article in service.list_articles(project_id)
    ]


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(
    article_id: str,
    service: ResearchServiceDependency,
) -> ArticleRead:
    return ArticleRead.model_validate(service.get_article(article_id))


@router.patch("/articles/{article_id}", response_model=ArticleRead)
def update_article(
    article_id: str,
    payload: ArticleUpdate,
    service: ResearchServiceDependency,
) -> ArticleRead:
    return ArticleRead.model_validate(service.update_article(article_id, payload))


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: str,
    service: ResearchServiceDependency,
) -> Response:
    service.delete_article(article_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/articles/{article_id}/references/extract",
    response_model=ReferencesResponse,
)
def extract_references(
    article_id: str,
    service: ResearchServiceDependency,
) -> ReferencesResponse:
    references = service.extract_references(article_id)
    return ReferencesResponse(
        article_id=article_id,
        status=(
            "EXTRACTED_PRELIMINARY"
            if references
            else "REFERENCES_SECTION_NOT_FOUND"
        ),
        references=[
            ReferenceRead.model_validate(reference) for reference in references
        ],
    )


@router.get(
    "/articles/{article_id}/references",
    response_model=ReferencesResponse,
)
def list_references(
    article_id: str,
    service: ResearchServiceDependency,
) -> ReferencesResponse:
    references = service.list_references(article_id)
    return ReferencesResponse(
        article_id=article_id,
        status="EXTRACTED_PRELIMINARY" if references else "REFERENCES_SECTION_NOT_FOUND",
        references=[
            ReferenceRead.model_validate(reference) for reference in references
        ],
    )


@router.post("/synthesis", response_model=SynthesisResponse)
def create_synthesis(
    payload: SynthesisRequest,
    service: ResearchSynthesisServiceDependency,
) -> SynthesisResponse:
    return service.synthesize(payload)


@router.post("/comparison", response_model=SynthesisResponse)
def create_comparison(
    payload: SynthesisRequest,
    service: ResearchSynthesisServiceDependency,
) -> SynthesisResponse:
    return service.synthesize(payload)


@router.post(
    "/doe/studies",
    response_model=DOEStudyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_doe_study(
    payload: DOEStudyCreate,
    service: ResearchServiceDependency,
) -> DOEStudyRead:
    return DOEStudyRead.model_validate(service.create_doe_study(payload))


@router.get("/doe/studies/{study_id}", response_model=DOEStudyRead)
def get_doe_study(
    study_id: str,
    service: ResearchServiceDependency,
) -> DOEStudyRead:
    return DOEStudyRead.model_validate(service.get_doe_study(study_id))


@router.post(
    "/anova/datasets",
    response_model=ANOVADatasetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_anova_dataset(
    payload: ANOVADatasetCreate,
    service: ResearchServiceDependency,
) -> ANOVADatasetRead:
    return ANOVADatasetRead.model_validate(service.create_anova_dataset(payload))


@router.get("/anova/datasets/{dataset_id}", response_model=ANOVADatasetRead)
def get_anova_dataset(
    dataset_id: str,
    service: ResearchServiceDependency,
) -> ANOVADatasetRead:
    return ANOVADatasetRead.model_validate(service.get_anova_dataset(dataset_id))


@router.post(
    "/reports",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    payload: ReportCreate,
    service: ResearchServiceDependency,
) -> ReportRead:
    return ReportRead.model_validate(service.create_report(payload))


@router.get("/reports", response_model=list[ReportRead])
def list_reports(
    project_id: str,
    service: ResearchServiceDependency,
) -> list[ReportRead]:
    return [
        ReportRead.model_validate(report)
        for report in service.list_reports(project_id)
    ]


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(
    report_id: str,
    service: ResearchServiceDependency,
) -> ReportRead:
    return ReportRead.model_validate(service.get_report(report_id))
