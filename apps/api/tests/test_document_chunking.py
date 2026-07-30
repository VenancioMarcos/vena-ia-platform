import pytest

from app.modules.documents.chunking import (
    CharacterTextChunker,
    InvalidChunkConfigurationError,
)


def test_splits_text_with_configured_overlap_and_offsets() -> None:
    chunker = CharacterTextChunker(chunk_size=12, overlap=3)

    chunks = chunker.split("alpha beta gamma delta")

    assert [chunk.content for chunk in chunks] == [
        "alpha beta",
        "eta gamma",
        "mma delta",
    ]
    assert [(chunk.start_offset, chunk.end_offset) for chunk in chunks] == [
        (0, 10),
        (7, 16),
        (13, 22),
    ]


def test_skips_empty_text() -> None:
    assert CharacterTextChunker(chunk_size=10, overlap=2).split(" \n ") == []


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (10, -1), (10, 10), (10, 11)],
)
def test_rejects_invalid_configuration(chunk_size: int, overlap: int) -> None:
    with pytest.raises(InvalidChunkConfigurationError):
        CharacterTextChunker(chunk_size=chunk_size, overlap=overlap)
