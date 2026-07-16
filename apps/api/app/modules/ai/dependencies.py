"""Request-scoped dependency construction for AI services."""

from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from packages.ai.providers import OpenAIProvider
from packages.ai.services import AIService, ProviderFactory


def get_provider_factory() -> ProviderFactory:
    return ProviderFactory(builders=(lambda: OpenAIProvider(settings.openai_api_key),))


def get_ai_service(
    provider_factory: Annotated[ProviderFactory, Depends(get_provider_factory)],
) -> AIService:
    return AIService(provider_factory)


AIServiceDependency = Annotated[AIService, Depends(get_ai_service)]
