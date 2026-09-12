from typing import Annotated

from fastapi import Depends, Request

from app.modules.cad.ingestion import CadIngestionGateway
from app.modules.cad.parser import StepTextParser
from app.modules.cad.service import CADAnalysisService
from app.modules.cad.services.step_processor import StepBackgroundProcessor
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


def get_cad_ingestion_gateway(request: Request) -> CadIngestionGateway:
    return request.app.state.cad_ingestion_gateway


CadIngestionGatewayDependency = Annotated[
    CadIngestionGateway,
    Depends(get_cad_ingestion_gateway),
]


def get_step_background_processor(
    gateway: CadIngestionGatewayDependency,
) -> StepBackgroundProcessor:
    return StepBackgroundProcessor(gateway)


StepBackgroundProcessorDependency = Annotated[
    StepBackgroundProcessor,
    Depends(get_step_background_processor),
]
