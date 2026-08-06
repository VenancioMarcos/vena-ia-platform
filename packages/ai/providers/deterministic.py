"""Local deterministic provider restricted to disposable integration environments."""

from __future__ import annotations

import hashlib
import time

from packages.ai.core import (
    AIProvider,
    BoundedConcurrencyGate,
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderCapability,
    ProviderInfo,
)


class DeterministicProvider(AIProvider):
    """No-network provider for repeatable CI process integration only."""

    name = "deterministic"

    def __init__(
        self,
        *,
        dimensions: int,
        delay_seconds: float,
        concurrency_gate: BoundedConcurrencyGate,
    ) -> None:
        self._dimensions = dimensions
        self._delay_seconds = delay_seconds
        self._gate = concurrency_gate

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            capabilities=[capability.value for capability in ProviderCapability],
            configured=True,
        )

    def _wait(self) -> None:
        with self._gate:
            time.sleep(self._delay_seconds)

    def chat(self, request: ChatRequest) -> ChatResult:
        self._wait()
        return ChatResult(
            provider=self.name,
            model=request.model or "deterministic-chat-v1",
            content="The indexed synthetic document contains controlled capacity evidence.",
        )

    def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResult:
        values = request.input if isinstance(request.input, list) else [request.input]
        self._wait()
        vectors: list[list[float]] = []
        for value in values:
            digest = hashlib.sha256(value.encode("utf-8")).digest()
            vectors.append(
                [
                    ((digest[index % len(digest)] / 255.0) * 2.0) - 1.0
                    for index in range(self._dimensions)
                ]
            )
        return EmbeddingsResult(
            provider=self.name,
            model=request.model or "deterministic-embedding-v1",
            embeddings=vectors,
        )

    def completion(self, request: CompletionRequest) -> CompletionResult:
        self._wait()
        return CompletionResult(
            provider=self.name,
            model=request.model or "deterministic-completion-v1",
            content="Controlled deterministic completion.",
        )
