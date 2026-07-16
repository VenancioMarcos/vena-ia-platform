"""Domain exceptions exposed by AI providers and services."""


class AIError(Exception):
    """Base exception for the AI abstraction layer."""


class ProviderNotFoundError(AIError):
    """Raised when a requested provider does not exist."""


class ProviderCapabilityError(AIError):
    """Raised when a provider does not support an operation."""


class AIExecutionError(AIError):
    """Raised when an upstream provider execution fails."""


class ProviderConfigurationError(AIError):
    """Raised when a provider is missing required configuration."""
