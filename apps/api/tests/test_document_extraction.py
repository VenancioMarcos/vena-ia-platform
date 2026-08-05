from unittest.mock import MagicMock

import pytest

from app.modules.documents.extraction import (
    PdfExtractionCancelled,
    PdfExtractionError,
    PdfTextExtractor,
)


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
    with pytest.raises(PdfExtractionError, match="valid PDF") as captured:
        PdfTextExtractor().extract_pages(b"not-a-pdf")
    assert captured.value.code == "PDF_INVALID"


def test_rejects_encrypted_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = MagicMock(is_encrypted=True, pages=[])
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader",
        lambda *_args, **_kwargs: reader,
    )

    with pytest.raises(PdfExtractionError, match="Encrypted") as captured:
        PdfTextExtractor().extract_pages(b"%PDF-1.7\nfixture")
    assert captured.value.code == "PDF_ENCRYPTED"


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

    with pytest.raises(PdfExtractionError, match="extractable text") as captured:
        PdfTextExtractor().extract_pages(b"%PDF-1.7\nfixture")
    assert captured.value.code == "PDF_NO_TEXT"


def test_many_page_synthetic_pdf_reports_monotonic_progress(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = []
    for index in range(500):
        page = MagicMock()
        page.extract_text.return_value = f"Synthetic page {index + 1}"
        pages.append(page)
    reader = MagicMock(is_encrypted=False, pages=pages)
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader", lambda *_args, **_kwargs: reader
    )
    progress: list[tuple[int, int]] = []

    extracted = PdfTextExtractor().extract_pages(
        b"%PDF-1.7\nsynthetic",
        page_progress=lambda current, total: progress.append((current, total)),
    )

    assert len(extracted) == 500
    assert progress[0] == (1, 500) and progress[-1] == (500, 500)
    assert progress == sorted(progress)


def test_many_page_extraction_can_cancel_between_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = []
    for index in range(100):
        page = MagicMock()
        page.extract_text.return_value = f"Synthetic page {index + 1}"
        pages.append(page)
    reader = MagicMock(is_encrypted=False, pages=pages)
    monkeypatch.setattr(
        "app.modules.documents.extraction.PdfReader", lambda *_args, **_kwargs: reader
    )
    completed = [0]

    with pytest.raises(PdfExtractionCancelled) as captured:
        PdfTextExtractor().extract_pages(
            b"%PDF-1.7\nsynthetic",
            page_progress=lambda current, _total: completed.__setitem__(0, current),
            cancelled=lambda: completed[0] >= 10,
        )

    assert completed[0] == 10
    assert captured.value.code == "JOB_CANCELLED"
