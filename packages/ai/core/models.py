"""Typed request and result objects shared across providers."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    model: str | None = None


class ChatResult(BaseModel):
    provider: str
    model: str
    content: str


class EmbeddingsRequest(BaseModel):
    input: str | list[str]
    model: str | None = None


class EmbeddingsResult(BaseModel):
    provider: str
    model: str
    embeddings: list[list[float]]


class CompletionRequest(BaseModel):
    prompt: str = Field(min_length=1)
    model: str | None = None


class CompletionResult(BaseModel):
    provider: str
    model: str
    content: str


class ProviderInfo(BaseModel):
    name: str
    capabilities: list[str]
    configured: bool
