"""Safe text extraction for validated PDF documents."""

from io import BytesIO

from pypdf import PdfReader

from app.modules.documents.contracts import ExtractedPage


class PdfExtractionError(Exception):
    pass


class PdfTextExtractor:
    def extract_pages(self, content: bytes) -> list[ExtractedPage]:
        if not content.startswith(b"%PDF-"):
            raise PdfExtractionError("Stored document is not a valid PDF")

        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise PdfExtractionError("Encrypted PDF documents are not supported")

            pages = [
                ExtractedPage(
                    page_number=page_number,
                    text=self._normalize(page.extract_text() or ""),
                )
                for page_number, page in enumerate(reader.pages, start=1)
            ]
        except PdfExtractionError:
            raise
        except Exception as exc:
            raise PdfExtractionError("Unable to extract text from PDF") from exc

        if not any(page.text for page in pages):
            raise PdfExtractionError("PDF does not contain extractable text")
        return pages

    @staticmethod
    def _normalize(text: str) -> str:
        lines = [" ".join(line.replace("\x00", "").split()) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)
