"""Configurable, page-preserving text chunking."""

from app.modules.documents.contracts import TextFragment


class InvalidChunkConfigurationError(ValueError):
    pass


class CharacterTextChunker:
    def __init__(self, chunk_size: int, overlap: int) -> None:
        if chunk_size <= 0:
            raise InvalidChunkConfigurationError("Chunk size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise InvalidChunkConfigurationError(
                "Chunk overlap must be non-negative and smaller than chunk size"
            )
        self._chunk_size = chunk_size
        self._overlap = overlap

    def split(self, text: str) -> list[TextFragment]:
        if not text.strip():
            return []

        fragments: list[TextFragment] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            hard_end = min(start + self._chunk_size, text_length)
            end = hard_end
            if hard_end < text_length:
                minimum_boundary = start + max(1, (self._chunk_size * 3) // 5)
                boundary = text.rfind(" ", minimum_boundary, hard_end)
                if boundary > start:
                    end = boundary

            content = text[start:end].strip()
            if content:
                leading_whitespace = len(text[start:end]) - len(text[start:end].lstrip())
                content_start = start + leading_whitespace
                fragments.append(
                    TextFragment(
                        content=content,
                        start_offset=content_start,
                        end_offset=content_start + len(content),
                    )
                )

            if end >= text_length:
                break
            next_start = end - self._overlap
            start = max(next_start, start + 1)

        return fragments
