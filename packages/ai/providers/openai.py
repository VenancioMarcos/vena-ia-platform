"""OpenAI HTTP adapter implemented without an SDK dependency."""

import json
import math
import socket
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from packages.ai.core import (
    AIExecutionError,
    BoundedConcurrencyGate,
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
    ClassifiedAIError,
    FailureClass,
    ResilienceBudget,
    execute_with_resilience,
)


class OpenAIProvider(AIProvider):
    """Adapter for OpenAI chat, Responses, and embeddings endpoints."""

    name = "openai"
    _base_url = "https://api.openai.com/v1"
    _default_text_model = "gpt-4o-mini"
    _default_embeddings_model = "text-embedding-3-small"

    def __init__(
        self,
        api_key: str,
        timeout_seconds: float | None = None,
        *,
        connect_timeout_seconds: float = 5.0,
        total_timeout_seconds: float = 30.0,
        max_attempts: int = 3,
        retry_base_seconds: float = 0.25,
        retry_max_seconds: float = 2.0,
        jitter_ratio: float = 0.2,
        concurrency_limit: int = 8,
        queue_timeout_seconds: float = 0.1,
        concurrency_gate: BoundedConcurrencyGate | None = None,
    ) -> None:
        self._api_key = api_key.strip()
        if timeout_seconds is not None:
            total_timeout_seconds = timeout_seconds
            connect_timeout_seconds = min(connect_timeout_seconds, timeout_seconds)
        self._connect_timeout_seconds = connect_timeout_seconds
        self._budget = ResilienceBudget(
            total_timeout_seconds,
            max_attempts,
            retry_base_seconds,
            retry_max_seconds,
            jitter_ratio,
        )
        self._gate = concurrency_gate or BoundedConcurrencyGate(
            concurrency_limit, queue_timeout_seconds
        )

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
        if not content.strip():
            raise AIExecutionError("OpenAI returned an empty chat response")
        return ChatResult(provider=self.name, model=model, content=content)

    def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResult:
        model = request.model or self._default_embeddings_model
        response = self._post("/embeddings", {"model": model, "input": request.input})
        try:
            embeddings = [cast(list[float], item["embedding"]) for item in response["data"]]
        except (KeyError, TypeError) as exc:
            raise AIExecutionError("OpenAI returned an invalid embeddings response") from exc
        expected = len(request.input) if isinstance(request.input, list) else 1
        if len(embeddings) != expected or any(
            not vector
            or any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in vector)
            for vector in embeddings
        ):
            raise AIExecutionError("OpenAI returned invalid embedding vectors")
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
        if not content.strip():
            raise AIExecutionError("OpenAI returned an empty completion response")
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
        with self._gate:
            body = execute_with_resilience(
                lambda remaining: self._request_once(request, remaining),
                self._budget,
            )
        if not isinstance(body, dict):
            raise AIExecutionError("OpenAI returned an invalid response")
        return cast(dict[str, Any], body)

    def _request_once(self, request: Request, remaining_seconds: float) -> object:
        timeout = min(self._connect_timeout_seconds, remaining_seconds)
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise self._classify_http_error(exc) from exc
        except json.JSONDecodeError as exc:
            raise ClassifiedAIError(
                "OpenAI returned an invalid response",
                FailureClass.INVALID_RESPONSE,
                retryable=False,
            ) from exc
        except URLError as exc:
            reason = exc.reason
            if isinstance(reason, socket.gaierror):
                failure = FailureClass.RESOLUTION
            elif isinstance(reason, ConnectionRefusedError):
                failure = FailureClass.CONNECTION_REFUSED
            elif isinstance(reason, (TimeoutError, socket.timeout)):
                failure = FailureClass.CONNECT_TIMEOUT
            else:
                failure = FailureClass.TEMPORARY_UNAVAILABLE
            raise ClassifiedAIError(
                "OpenAI dependency is temporarily unavailable", failure, retryable=True
            ) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise ClassifiedAIError(
                "OpenAI response timed out", FailureClass.READ_TIMEOUT, retryable=True
            ) from exc
        except OSError as exc:
            raise ClassifiedAIError(
                "OpenAI dependency is temporarily unavailable",
                FailureClass.TEMPORARY_UNAVAILABLE,
                retryable=True,
            ) from exc

    @staticmethod
    def _classify_http_error(exc: HTTPError) -> ClassifiedAIError:
        status = exc.code
        mapping = {
            401: (FailureClass.AUTHENTICATION, False),
            403: (FailureClass.AUTHORIZATION, False),
            404: (FailureClass.NOT_FOUND, False),
            409: (FailureClass.CONFLICT, False),
            422: (FailureClass.INVALID_PAYLOAD, False),
            429: (FailureClass.RATE_LIMIT, True),
            502: (FailureClass.TEMPORARY_UNAVAILABLE, True),
            503: (FailureClass.TEMPORARY_UNAVAILABLE, True),
            504: (FailureClass.TEMPORARY_UNAVAILABLE, True),
        }
        failure, retryable = mapping.get(status, (FailureClass.PERMANENT, False))
        return ClassifiedAIError(
            "OpenAI request failed safely",
            failure,
            retryable=retryable,
            retry_after_seconds=OpenAIProvider._retry_after(exc),
        )

    @staticmethod
    def _retry_after(exc: HTTPError) -> float | None:
        raw = exc.headers.get("Retry-After") if exc.headers else None
        if not raw:
            return None
        try:
            return max(0.0, min(float(raw), 60.0))
        except ValueError:
            try:
                value = (parsedate_to_datetime(raw) - datetime.now(timezone.utc)).total_seconds()
                return max(0.0, min(value, 60.0))
            except (TypeError, ValueError):
                return None
