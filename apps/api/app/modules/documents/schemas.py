from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class DocumentCreate(BaseModel):
    project_id: str = Field(min_length=1)
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    file_size: int = Field(ge=0)
    storage_path: str = Field(min_length=1, max_length=500)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    status: DocumentStatus
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentCountResponse(BaseModel):
    project_id: str
    count: int


class DocumentStatisticsResponse(BaseModel):
    total_documents: int
    uploaded: int
    processing: int
    ready: int
    failed: int
    total_storage_bytes: int


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    page_number: int
    chunk_index: int
    start_offset: int
    end_offset: int
    character_count: int
    content: str
    created_at: datetime


class DocumentChunkListResponse(BaseModel):
    chunks: list[DocumentChunkResponse]
    total: int


class DocumentProcessingResponse(BaseModel):
    document: DocumentResponse
    chunk_count: int


class DocumentEmbeddingResponse(BaseModel):
    document_id: str
    embedded_chunks: int
    model: str


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4_000)
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeMatchResponse(BaseModel):
    document_id: str
    page_number: int
    chunk_index: int
    content: str
    score: float


class KnowledgeSearchResponse(BaseModel):
    project_id: str
    query: str
    matches: list[KnowledgeMatchResponse]


class KnowledgeAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeAnswerResponse(BaseModel):
    project_id: str
    question: str
    answer: str
    provider: str
    model: str
    matches: list[KnowledgeMatchResponse]
