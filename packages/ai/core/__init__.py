"""Public contracts for the AI abstraction layer."""

from packages.ai.core.exceptions import (
    AIExecutionError,
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderNotFoundError,
)
from packages.ai.core.models import (
    ChatMessage,
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderInfo,
)
from packages.ai.core.provider import AIProvider, ProviderCapability

__all__ = [
    "AIExecutionError",
    "AIProvider",
    "ChatMessage",
    "ChatRequest",
    "ChatResult",
    "CompletionRequest",
    "CompletionResult",
    "EmbeddingsRequest",
    "EmbeddingsResult",
    "ProviderCapability",
    "ProviderCapabilityError",
    "ProviderConfigurationError",
    "ProviderInfo",
    "ProviderNotFoundError",
]
