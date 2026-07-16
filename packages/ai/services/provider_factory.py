"""Provider construction without a process-wide registry."""

from collections.abc import Callable

from packages.ai.core import AIProvider, ProviderNotFoundError

ProviderBuilder = Callable[[], AIProvider]


class ProviderFactory:
    """Build providers from request-scoped constructor dependencies."""

    def __init__(self, builders: tuple[ProviderBuilder, ...]) -> None:
        self._builders = builders

    def create(self, name: str) -> AIProvider:
        for builder in self._builders:
            provider = builder()
            if provider.info.name == name:
                return provider
        raise ProviderNotFoundError(f"AI provider '{name}' was not found")

    def list_providers(self) -> list[AIProvider]:
        return [builder() for builder in self._builders]
