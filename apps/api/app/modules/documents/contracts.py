"""Contracts for document text extraction, chunking, and processing."""

from dataclasses import dataclass
from typing import Protocol

from app.modules.documents.models import Document, DocumentChunk


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class TextFragment:
    content: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True)
class ProcessingResult:
    document: Document
    chunk_count: int


class TextExtractor(Protocol):
    def extract_pages(self, content: bytes) -> list[ExtractedPage]: ...


class ChunkingStrategy(Protocol):
    def split(self, text: str) -> list[TextFragment]: ...


class ChunkRepositoryContract(Protocol):
    def replace_for_document(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]: ...

    def list_for_document(
        self,
        document_id: str,
        page_number: int | None = None,
    ) -> list[DocumentChunk]: ...


class DocumentProcessingServiceContract(Protocol):
    def process(self, document_id: str) -> ProcessingResult: ...

    def list_chunks(
        self,
        document_id: str,
        page_number: int | None = None,
    ) -> list[DocumentChunk]: ...
