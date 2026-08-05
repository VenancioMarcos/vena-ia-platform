"""Safe text extraction for validated PDF documents."""

from collections.abc import Callable
from io import BytesIO

from pypdf import PdfReader

from app.modules.documents.contracts import ExtractedPage


class PdfExtractionError(Exception):
    def __init__(self, message: str, *, code: str = "PDF_INVALID") -> None:
        super().__init__(message)
        self.code = code


class PdfExtractionCancelled(PdfExtractionError):
    def __init__(self) -> None:
        super().__init__("PDF extraction was cancelled", code="JOB_CANCELLED")


class PdfTextExtractor:
    def extract_pages(
        self,
        content: bytes,
        *,
        page_progress: Callable[[int, int], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> list[ExtractedPage]:
        if not content.startswith(b"%PDF-"):
            raise PdfExtractionError("Stored document is not a valid PDF", code="PDF_INVALID")

        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise PdfExtractionError(
                    "Encrypted PDF documents are not supported", code="PDF_ENCRYPTED"
                )

            total = len(reader.pages)
            pages: list[ExtractedPage] = []
            for page_number, page in enumerate(reader.pages, start=1):
                if cancelled is not None and cancelled():
                    raise PdfExtractionCancelled
                pages.append(
                    ExtractedPage(
                        page_number=page_number,
                        text=self._normalize(page.extract_text() or ""),
                    )
                )
                if page_progress is not None:
                    page_progress(page_number, total)
        except PdfExtractionError:
            raise
        except Exception as exc:
            raise PdfExtractionError("Unable to extract text from PDF", code="PDF_INVALID") from exc

        if not any(page.text for page in pages):
            raise PdfExtractionError("PDF does not contain extractable text", code="PDF_NO_TEXT")
        return pages

    @staticmethod
    def _normalize(text: str) -> str:
        lines = [" ".join(line.replace("\x00", "").split()) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)
