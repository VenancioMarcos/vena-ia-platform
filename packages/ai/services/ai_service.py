"""Capability-aware facade over AI providers."""

from packages.ai.core import (
    AIProvider,
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderCapability,
    ProviderCapabilityError,
    ProviderInfo,
)
from packages.ai.services.provider_factory import ProviderFactory


class AIService:
    def __init__(self, provider_factory: ProviderFactory) -> None:
        self._provider_factory = provider_factory

    def providers(self) -> list[ProviderInfo]:
        return [provider.info for provider in self._provider_factory.list_providers()]

    def chat(self, provider_name: str, request: ChatRequest) -> ChatResult:
        provider = self._provider(provider_name, ProviderCapability.CHAT)
        return provider.chat(request)

    def embeddings(
        self, provider_name: str, request: EmbeddingsRequest
    ) -> EmbeddingsResult:
        provider = self._provider(provider_name, ProviderCapability.EMBEDDINGS)
        return provider.embeddings(request)

    def completion(
        self, provider_name: str, request: CompletionRequest
    ) -> CompletionResult:
        provider = self._provider(provider_name, ProviderCapability.COMPLETION)
        return provider.completion(request)

    def _provider(self, provider_name: str, capability: ProviderCapability) -> AIProvider:
        provider = self._provider_factory.create(provider_name)
        if capability.value not in provider.info.capabilities:
            raise ProviderCapabilityError(
                f"AI provider '{provider_name}' does not support '{capability.value}'"
            )
        return provider
