"""OpenAI HTTP adapter implemented without an SDK dependency."""

import json
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from packages.ai.core import (
    AIExecutionError,
    AIProvider,
    ChatRequest,
    ChatResult,
    CompletionRequest,
    CompletionResult,
    EmbeddingsRequest,
    EmbeddingsResult,
    ProviderCapability,
    ProviderConfigurationError,
    ProviderInfo,
)


class OpenAIProvider(AIProvider):
    """Adapter for OpenAI chat, Responses, and embeddings endpoints."""

    name = "openai"
    _base_url = "https://api.openai.com/v1"
    _default_text_model = "gpt-4o-mini"
    _default_embeddings_model = "text-embedding-3-small"

    def __init__(self, api_key: str, timeout_seconds: float = 30.0) -> None:
        self._api_key = api_key.strip()
        self._timeout_seconds = timeout_seconds

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            capabilities=[capability.value for capability in ProviderCapability],
            configured=bool(self._api_key),
        )

    def chat(self, request: ChatRequest) -> ChatResult:
        model = request.model or self._default_text_model
        payload = {
            "model": model,
            "messages": [message.model_dump() for message in request.messages],
        }
        response = self._post("/chat/completions", payload)
        try:
            content = cast(str, response["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AIExecutionError("OpenAI returned an invalid chat response") from exc
        return ChatResult(provider=self.name, model=model, content=content)

    def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResult:
        model = request.model or self._default_embeddings_model
        response = self._post("/embeddings", {"model": model, "input": request.input})
        try:
            embeddings = [cast(list[float], item["embedding"]) for item in response["data"]]
        except (KeyError, TypeError) as exc:
            raise AIExecutionError("OpenAI returned an invalid embeddings response") from exc
        return EmbeddingsResult(provider=self.name, model=model, embeddings=embeddings)

    def completion(self, request: CompletionRequest) -> CompletionResult:
        model = request.model or self._default_text_model
        response = self._post("/responses", {"model": model, "input": request.prompt})
        content = response.get("output_text")
        if not isinstance(content, str):
            try:
                content = cast(str, response["output"][0]["content"][0]["text"])
            except (KeyError, IndexError, TypeError) as exc:
                raise AIExecutionError(
                    "OpenAI returned an invalid completion response"
                ) from exc
        return CompletionResult(provider=self.name, model=model, content=content)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise ProviderConfigurationError("OpenAI API key is not configured")

        request = Request(
            f"{self._base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:  # noqa: S310
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            raise AIExecutionError("OpenAI request failed") from exc
        if not isinstance(body, dict):
            raise AIExecutionError("OpenAI returned an invalid response")
        return cast(dict[str, Any], body)
