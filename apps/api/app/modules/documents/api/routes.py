from collections.abc import Callable, Sequence
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

from app.modules.documents.dependencies import DocumentServiceDependency
from app.modules.documents.models import Document
from app.modules.documents.schemas import (
    DocumentCountResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatisticsResponse,
)
from app.modules.documents.pipeline import InvalidDocumentTransitionError
from app.modules.documents.service import (
    DocumentAccessDeniedError,
    DocumentAdministrationDeniedError,
    DocumentNotFoundError,
    DocumentProjectMismatchError,
    DocumentStorageError,
    DocumentTooLargeError,
    InvalidDocumentError,
    ProjectNotFoundError,
)

router = APIRouter(tags=["documents"])


def _not_found(exc: DocumentNotFoundError | ProjectNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


def _document_list(documents: Sequence[Document]) -> DocumentListResponse:
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(document) for document in documents],
        total=len(documents),
    )


def _administrative_list(
    operation: Callable[[], list[Document]],
) -> DocumentListResponse:
    try:
        return _document_list(operation())
    except DocumentAdministrationDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    project_id: str,
    file: Annotated[UploadFile, File()],
    service: DocumentServiceDependency,
) -> DocumentResponse:
    try:
        return DocumentResponse.model_validate(service.create(project_id, file))
    except ProjectNotFoundError as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DocumentStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/projects/{project_id}/documents", response_model=DocumentListResponse)
def list_documents(
    project_id: str, service: DocumentServiceDependency
) -> DocumentListResponse:
    try:
        documents = service.list_documents(project_id)
    except ProjectNotFoundError as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return _document_list(documents)


@router.get(
    "/projects/{project_id}/documents/count",
    response_model=DocumentCountResponse,
)
def count_documents(
    project_id: str, service: DocumentServiceDependency
) -> DocumentCountResponse:
    try:
        count = service.count_documents(project_id)
    except ProjectNotFoundError as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return DocumentCountResponse(project_id=project_id, count=count)


@router.get("/documents", response_model=DocumentListResponse)
def list_all_documents(service: DocumentServiceDependency) -> DocumentListResponse:
    return _administrative_list(service.list_all_documents)


@router.get("/documents/status/ready", response_model=DocumentListResponse)
def list_ready_documents(service: DocumentServiceDependency) -> DocumentListResponse:
    return _administrative_list(service.list_ready_documents)


@router.get("/documents/status/processing", response_model=DocumentListResponse)
def list_processing_documents(service: DocumentServiceDependency) -> DocumentListResponse:
    return _administrative_list(service.list_processing_documents)


@router.get("/documents/status/failed", response_model=DocumentListResponse)
def list_failed_documents(service: DocumentServiceDependency) -> DocumentListResponse:
    return _administrative_list(service.list_failed_documents)


@router.get("/documents/statistics", response_model=DocumentStatisticsResponse)
def document_statistics(
    service: DocumentServiceDependency,
) -> DocumentStatisticsResponse:
    try:
        return DocumentStatisticsResponse.model_validate(service.document_statistics())
    except DocumentAdministrationDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str, service: DocumentServiceDependency
) -> DocumentResponse:
    try:
        return DocumentResponse.model_validate(service.get(document_id))
    except DocumentNotFoundError as exc:
        raise _not_found(exc) from exc
    except ProjectNotFoundError as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, service: DocumentServiceDependency) -> Response:
    try:
        service.delete(document_id)
    except ProjectNotFoundError as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DocumentStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/projects/{project_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_document(
    project_id: str,
    document_id: str,
    service: DocumentServiceDependency,
) -> Response:
    try:
        service.remove_document(project_id, document_id)
    except (ProjectNotFoundError, DocumentNotFoundError) as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DocumentProjectMismatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DocumentStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/documents/{document_id}/process", response_model=DocumentResponse)
def process_document(
    document_id: str, service: DocumentServiceDependency
) -> DocumentResponse:
    try:
        return DocumentResponse.model_validate(service.process_document(document_id))
    except (DocumentNotFoundError, ProjectNotFoundError) as exc:
        raise _not_found(exc) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except InvalidDocumentTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
