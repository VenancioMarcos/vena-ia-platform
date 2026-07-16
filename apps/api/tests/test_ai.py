from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai.dependencies import get_provider_factory
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
from packages.ai.services import ProviderFactory


class FakeProvider(AIProvider):
    name = "fake"

    def __init__(
        self,
        capabilities: tuple[ProviderCapability, ...] = tuple(ProviderCapability),
        error: Exception | None = None,
    ) -> None:
        self._capabilities = capabilities
        self._error = error

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            capabilities=[capability.value for capability in self._capabilities],
            configured=True,
        )

    def _raise_error(self) -> None:
        if self._error:
            raise self._error

    def chat(self, request: ChatRequest) -> ChatResult:
        self._raise_error()
        return ChatResult(provider=self.name, model=request.model or "fake-chat", content="reply")

    def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResult:
        self._raise_error()
        return EmbeddingsResult(
            provider=self.name,
            model=request.model or "fake-embeddings",
            embeddings=[[0.1, 0.2]],
        )

    def completion(self, request: CompletionRequest) -> CompletionResult:
        self._raise_error()
        return CompletionResult(
            provider=self.name,
            model=request.model or "fake-completion",
            content="completed",
        )


@pytest.fixture()
def override_provider() -> Generator[Callable[[AIProvider], TestClient], None, None]:
    original_overrides = app.dependency_overrides.copy()

    def apply(provider: AIProvider) -> TestClient:
        app.dependency_overrides[get_provider_factory] = lambda: ProviderFactory(
            builders=(lambda: provider,)
        )
        return TestClient(app)

    yield apply
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


def test_list_providers(override_provider: Callable[[AIProvider], TestClient]) -> None:
    response = override_provider(FakeProvider()).get("/ai/providers")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "fake",
            "capabilities": ["chat", "embeddings", "completion"],
            "configured": True,
        }
    ]


def test_chat(override_provider: Callable[[AIProvider], TestClient]) -> None:
    response = override_provider(FakeProvider()).post(
        "/ai/fake/chat", json={"messages": [{"role": "user", "content": "Hello"}]}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "reply"


def test_embeddings(override_provider: Callable[[AIProvider], TestClient]) -> None:
    response = override_provider(FakeProvider()).post(
        "/ai/fake/embeddings", json={"input": "bearing preload"}
    )

    assert response.status_code == 200
    assert response.json()["embeddings"] == [[0.1, 0.2]]


def test_completion(override_provider: Callable[[AIProvider], TestClient]) -> None:
    response = override_provider(FakeProvider()).post(
        "/ai/fake/completion", json={"prompt": "Complete this"}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "completed"


def test_unknown_provider_returns_404(
    override_provider: Callable[[AIProvider], TestClient],
) -> None:
    response = override_provider(FakeProvider()).post(
        "/ai/unknown/chat", json={"messages": [{"role": "user", "content": "Hello"}]}
    )

    assert response.status_code == 404


def test_unsupported_capability_returns_400(
    override_provider: Callable[[AIProvider], TestClient],
) -> None:
    provider = FakeProvider(capabilities=(ProviderCapability.CHAT,))
    response = override_provider(provider).post(
        "/ai/fake/embeddings", json={"input": "bearing preload"}
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (AIExecutionError("upstream failed"), 502),
        (ProviderConfigurationError("provider is not configured"), 503),
    ],
)
def test_provider_errors_are_mapped(
    override_provider: Callable[[AIProvider], TestClient],
    error: Exception,
    expected_status: int,
) -> None:
    response = override_provider(FakeProvider(error=error)).post(
        "/ai/fake/chat", json={"messages": [{"role": "user", "content": "Hello"}]}
    )

    assert response.status_code == expected_status


def test_dependency_override_is_cleaned() -> None:
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_provider_factory] = lambda: ProviderFactory(
        builders=(FakeProvider,)
    )

    try:
        assert get_provider_factory in app.dependency_overrides
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

    assert get_provider_factory not in app.dependency_overrides
