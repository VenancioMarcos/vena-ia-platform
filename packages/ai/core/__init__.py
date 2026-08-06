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
from packages.ai.core.resilience import (
    AIBackpressureError,
    BoundedConcurrencyGate,
    ClassifiedAIError,
    FailureClass,
    ResilienceBudget,
    execute_with_resilience,
)

__all__ = [
    "AIExecutionError",
    "AIBackpressureError",
    "AIProvider",
    "ChatMessage",
    "ChatRequest",
    "ChatResult",
    "BoundedConcurrencyGate",
    "ClassifiedAIError",
    "CompletionRequest",
    "CompletionResult",
    "EmbeddingsRequest",
    "EmbeddingsResult",
    "FailureClass",
    "ProviderCapability",
    "ProviderCapabilityError",
    "ProviderConfigurationError",
    "ProviderInfo",
    "ProviderNotFoundError",
    "ResilienceBudget",
    "execute_with_resilience",
]
