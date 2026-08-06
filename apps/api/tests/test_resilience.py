from email.message import Message
from urllib.error import HTTPError

import pytest

from app.core.config import Settings
from packages.ai.core import (
    AIBackpressureError,
    BoundedConcurrencyGate,
    ClassifiedAIError,
    FailureClass,
    ResilienceBudget,
    execute_with_resilience,
)
from packages.ai.providers.openai import OpenAIProvider


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


def test_retry_budget_is_bounded_and_deterministic() -> None:
    budget = ResilienceBudget(10, 3, 1, 2, 0.2)
    assert budget.delay(1, 0) == pytest.approx(0.8)
    assert budget.delay(2, 0.5) == pytest.approx(2)
    assert budget.delay(3, 1) == pytest.approx(2)


@pytest.mark.parametrize(
    "budget",
    [
        (0, 1, 0, 0, 0),
        (1, 0, 0, 0, 0),
        (1, 1, 2, 1, 0),
        (1, 1, 0, 1, 2),
    ],
)
def test_invalid_retry_budget_fails_closed(budget: tuple[float, int, float, float, float]) -> None:
    with pytest.raises(ValueError):
        ResilienceBudget(*budget)


def test_retry_recovers_within_global_deadline() -> None:
    clock = FakeClock()
    attempts = 0

    def operation(_remaining: float) -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ClassifiedAIError(
                "temporary", FailureClass.TEMPORARY_UNAVAILABLE, retryable=True
            )
        return "ready"

    result = execute_with_resilience(
        operation,
        ResilienceBudget(10, 3, 1, 2, 0),
        monotonic=clock.monotonic,
        sleeper=clock.sleep,
        random_unit=lambda: 0.5,
    )
    assert result == "ready"
    assert attempts == 3
    assert clock.sleeps == [1, 2]


def test_non_retryable_failure_is_not_repeated() -> None:
    attempts = 0

    def operation(_remaining: float) -> None:
        nonlocal attempts
        attempts += 1
        raise ClassifiedAIError("invalid", FailureClass.INVALID_RESPONSE, retryable=False)

    with pytest.raises(ClassifiedAIError) as raised:
        execute_with_resilience(operation, ResilienceBudget(10, 3, 1, 2, 0))
    assert raised.value.failure_class == FailureClass.INVALID_RESPONSE
    assert attempts == 1


def test_retry_after_cannot_exceed_budget() -> None:
    clock = FakeClock()

    def operation(_remaining: float) -> None:
        raise ClassifiedAIError(
            "limited", FailureClass.RATE_LIMIT, retryable=True, retry_after_seconds=60
        )

    with pytest.raises(ClassifiedAIError) as raised:
        execute_with_resilience(
            operation,
            ResilienceBudget(1, 3, 0.1, 2, 0),
            monotonic=clock.monotonic,
            sleeper=clock.sleep,
        )
    assert raised.value.failure_class == FailureClass.EXHAUSTED
    assert clock.sleeps == []


def test_concurrency_gate_rejects_without_unbounded_queue() -> None:
    gate = BoundedConcurrencyGate(1, 0)
    with gate:
        with pytest.raises(AIBackpressureError):
            with gate:
                pass


def test_http_failure_classification_respects_retry_after() -> None:
    headers = Message()
    headers["Retry-After"] = "3"
    error = HTTPError("https://example.invalid", 429, "limited", headers, None)
    classified = OpenAIProvider._classify_http_error(error)
    assert classified.failure_class == FailureClass.RATE_LIMIT
    assert classified.retryable is True
    assert classified.retry_after_seconds == 3


@pytest.mark.parametrize(
    "values",
    [
        {"ai_connect_timeout_seconds": 31},
        {"ai_connect_timeout_seconds": 10, "ai_total_timeout_seconds": 5},
        {"ai_retry_base_seconds": 3, "ai_retry_max_seconds": 2},
        {"jobs_retry_base_seconds": 301, "jobs_retry_max_seconds": 300},
        {"ai_concurrency_limit": 0},
    ],
)
def test_invalid_resilience_settings_fail_at_startup(values: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, **values)
