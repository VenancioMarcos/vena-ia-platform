from typing import Annotated

from fastapi import Depends

from app.modules.cad.parser import StepTextParser
from app.modules.cad.service import CADAnalysisService
from app.modules.documents.dependencies import (
    DocumentServiceDependency,
    DocumentStorageDependency,
)


def get_step_parser() -> StepTextParser:
    return StepTextParser()


def get_cad_analysis_service(
    documents: DocumentServiceDependency,
    storage: DocumentStorageDependency,
    parser: Annotated[StepTextParser, Depends(get_step_parser)],
) -> CADAnalysisService:
    return CADAnalysisService(documents, storage, parser)


CADAnalysisServiceDependency = Annotated[
    CADAnalysisService,
    Depends(get_cad_analysis_service),
]
