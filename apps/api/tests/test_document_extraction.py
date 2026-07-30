from unittest.mock import MagicMock

import pytest

from app.modules.documents.extraction import PdfExtractionError, PdfTextExtractor


def test_extracts_and_normalizes_page_text(monkeypatch: pytest.MonkeyPatch) -> None:
    first_page = MagicMock()
    first_page.extract_text.return_value = "  First   line\nSecond\x00 line "
    second_page = MagicMock()
    second_page.extract_text.return_value = "Page two"
    reader = MagicMock(is_encrypted=False, pages=[first_page, second_page])
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader",
        lambda *_args, **_kwargs: reader,
    )

    pages = PdfTextExtractor().extract_pages(b"%PDF-1.7\nfixture")

    assert [(page.page_number, page.text) for page in pages] == [
        (1, "First line\nSecond line"),
        (2, "Page two"),
    ]


def test_rejects_non_pdf_content() -> None:
    with pytest.raises(PdfExtractionError, match="valid PDF"):
        PdfTextExtractor().extract_pages(b"not-a-pdf")


def test_rejects_encrypted_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = MagicMock(is_encrypted=True, pages=[])
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader",
        lambda *_args, **_kwargs: reader,
    )

    with pytest.raises(PdfExtractionError, match="Encrypted"):
        PdfTextExtractor().extract_pages(b"%PDF-1.7\nfixture")


def test_rejects_pdf_without_extractable_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = MagicMock()
    page.extract_text.return_value = " \n "
    reader = MagicMock(is_encrypted=False, pages=[page])
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader",
        lambda *_args, **_kwargs: reader,
    )

    with pytest.raises(PdfExtractionError, match="extractable text"):
        PdfTextExtractor().extract_pages(b"%PDF-1.7\nfixture")
