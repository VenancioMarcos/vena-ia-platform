"""Provider-agnostic AI HTTP endpoints."""

from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, HTTPException

from app.modules.ai.dependencies import AIServiceDependency
from packages.ai.core import (
    AIExecutionError,
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderInfo,
    ProviderNotFoundError,
)

router = APIRouter(prefix="/ai", tags=["ai"])
ResultT = TypeVar("ResultT")


def _execute(operation: Callable[[], ResultT]) -> ResultT:
    try:
        return operation()
    except ProviderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderCapabilityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AIExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/providers", response_model=list[ProviderInfo])
def list_providers(service: AIServiceDependency) -> list[ProviderInfo]:
    return service.providers()


@router.post("/{provider}/chat", response_model=ChatResult)
def chat(provider: str, payload: ChatRequest, service: AIServiceDependency) -> ChatResult:
    return _execute(lambda: service.chat(provider, payload))


@router.post("/{provider}/embeddings", response_model=EmbeddingsResult)
def embeddings(
    provider: str, payload: EmbeddingsRequest, service: AIServiceDependency
) -> EmbeddingsResult:
    return _execute(lambda: service.embeddings(provider, payload))


@router.post("/{provider}/completion", response_model=CompletionResult)
def completion(
    provider: str, payload: CompletionRequest, service: AIServiceDependency
) -> CompletionResult:
    return _execute(lambda: service.completion(provider, payload))
