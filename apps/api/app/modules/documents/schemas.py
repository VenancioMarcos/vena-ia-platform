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
