"""Request-scoped dependency construction for AI services."""

from functools import lru_cache
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from packages.ai.core import AIProvider, BoundedConcurrencyGate
from packages.ai.providers import DeterministicProvider, OpenAIProvider
from packages.ai.services import AIService, ProviderFactory


@lru_cache(maxsize=8)
def _ai_concurrency_gate(limit: int, queue_timeout: float) -> BoundedConcurrencyGate:
    return BoundedConcurrencyGate(limit, queue_timeout)


def get_provider_factory() -> ProviderFactory:
    builders: list[Callable[[], AIProvider]] = [
        lambda: OpenAIProvider(
            settings.openai_api_key,
            connect_timeout_seconds=settings.ai_connect_timeout_seconds,
            total_timeout_seconds=settings.ai_total_timeout_seconds,
            max_attempts=settings.ai_max_attempts,
            retry_base_seconds=settings.ai_retry_base_seconds,
            retry_max_seconds=settings.ai_retry_max_seconds,
            jitter_ratio=settings.ai_retry_jitter_ratio,
            concurrency_limit=settings.ai_concurrency_limit,
            queue_timeout_seconds=settings.ai_queue_timeout_seconds,
            concurrency_gate=_ai_concurrency_gate(
                settings.ai_concurrency_limit, settings.ai_queue_timeout_seconds
            ),
        )
    ]
    if settings.app_env == "capacity-ci":
        builders.append(
            lambda: DeterministicProvider(
                dimensions=settings.rag_embedding_dimensions,
                delay_seconds=settings.deterministic_ai_delay_seconds,
                concurrency_gate=_ai_concurrency_gate(
                    settings.ai_concurrency_limit, settings.ai_queue_timeout_seconds
                ),
            )
        )
    return ProviderFactory(builders=tuple(builders))


def get_ai_service(
    provider_factory: Annotated[ProviderFactory, Depends(get_provider_factory)],
) -> AIService:
    return AIService(provider_factory)


AIServiceDependency = Annotated[AIService, Depends(get_ai_service)]
