"""Provider interface for all AI integrations."""

from abc import ABC, abstractmethod
from enum import StrEnum

from packages.ai.core.models import (
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderInfo,
)


class ProviderCapability(StrEnum):
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    COMPLETION = "completion"


class AIProvider(ABC):
    """Contract implemented by concrete AI providers."""

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Return provider metadata without executing a remote request."""

    @abstractmethod
    def chat(self, request: ChatRequest) -> ChatResult:
        """Generate a response for a sequence of chat messages."""

    @abstractmethod
    def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResult:
        """Generate embeddings for one or more text inputs."""

    @abstractmethod
    def completion(self, request: CompletionRequest) -> CompletionResult:
        """Generate a text completion for a prompt."""
