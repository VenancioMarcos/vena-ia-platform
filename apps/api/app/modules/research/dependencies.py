from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import AuthorizationDependency
from app.modules.documents.dependencies import (
    DocumentChunkRepositoryDependency,
    KnowledgeServiceDependency,
)
from app.modules.research.repository import ResearchRepository
from app.modules.research.service import ResearchService, ResearchSynthesisService


def get_research_repository(db: Annotated[Session, Depends(get_db)]) -> ResearchRepository:
    return ResearchRepository(db)


ResearchRepositoryDependency = Annotated[
    ResearchRepository, Depends(get_research_repository)
]


def get_research_service(
    db: Annotated[Session, Depends(get_db)],
    authorization: AuthorizationDependency,
    repository: ResearchRepositoryDependency,
    chunk_repository: DocumentChunkRepositoryDependency,
) -> ResearchService:
    return ResearchService(db, authorization, repository, chunk_repository)


ResearchServiceDependency = Annotated[ResearchService, Depends(get_research_service)]


def get_research_synthesis_service(
    knowledge: KnowledgeServiceDependency,
) -> ResearchSynthesisService:
    return ResearchSynthesisService(knowledge)


ResearchSynthesisServiceDependency = Annotated[
    ResearchSynthesisService, Depends(get_research_synthesis_service)
]
