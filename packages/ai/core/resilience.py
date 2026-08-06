"""Bounded resilience primitives for external AI operations."""

from __future__ import annotations

import math
import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from packages.ai.core.exceptions import AIExecutionError

ResultT = TypeVar("ResultT")


class FailureClass(StrEnum):
    CONNECT_TIMEOUT = "connect_timeout"
    READ_TIMEOUT = "read_timeout"
    TOTAL_TIMEOUT = "total_timeout"
    CONNECTION_REFUSED = "connection_refused"
    RESOLUTION = "resolution"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_UNAVAILABLE = "temporary_unavailable"
    PERMANENT = "permanent"
    INVALID_PAYLOAD = "invalid_payload"
    INVALID_RESPONSE = "invalid_response"
    CONFLICT = "conflict"
    NOT_FOUND = "not_found"
    CANCELLED = "cancelled"
    EXHAUSTED = "exhausted"
    INTERNAL = "internal"


@dataclass(frozen=True, slots=True)
class ResilienceBudget:
    total_timeout_seconds: float
    max_attempts: int
    retry_base_seconds: float
    retry_max_seconds: float
    jitter_ratio: float = 0.2

    def __post_init__(self) -> None:
        values = (
            self.total_timeout_seconds,
            self.retry_base_seconds,
            self.retry_max_seconds,
            self.jitter_ratio,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Resilience budget values must be finite")
        if self.total_timeout_seconds <= 0 or not 1 <= self.max_attempts <= 10:
            raise ValueError("Resilience timeout and attempts are outside safe bounds")
        if self.retry_base_seconds < 0 or self.retry_max_seconds < self.retry_base_seconds:
            raise ValueError("Retry backoff bounds are invalid")
        if not 0 <= self.jitter_ratio <= 1:
            raise ValueError("Retry jitter ratio must be between zero and one")

    def delay(self, failed_attempt: int, random_unit: float) -> float:
        if not 0 <= random_unit <= 1:
            raise ValueError("Random unit must be between zero and one")
        base = min(
            self.retry_base_seconds * (2 ** max(failed_attempt - 1, 0)),
            self.retry_max_seconds,
        )
        jitter = base * self.jitter_ratio * ((2 * random_unit) - 1)
        return max(0.0, min(base + jitter, self.retry_max_seconds))


class ClassifiedAIError(AIExecutionError):
    def __init__(
        self,
        safe_message: str,
        failure_class: FailureClass,
        *,
        retryable: bool,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.failure_class = failure_class
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds


class AIBackpressureError(ClassifiedAIError):
    def __init__(self) -> None:
        super().__init__(
            "AI provider concurrency limit reached",
            FailureClass.TEMPORARY_UNAVAILABLE,
            retryable=True,
            retry_after_seconds=1,
        )


class BoundedConcurrencyGate:
    """Per-process gate with bounded wait; no unbounded in-memory queue."""

    def __init__(self, limit: int, queue_timeout_seconds: float) -> None:
        if not 1 <= limit <= 1_000 or not 0 <= queue_timeout_seconds <= 30:
            raise ValueError("Concurrency gate values are outside safe bounds")
        self._semaphore = threading.BoundedSemaphore(limit)
        self._queue_timeout = queue_timeout_seconds

    def __enter__(self) -> None:
        if not self._semaphore.acquire(timeout=self._queue_timeout):
            raise AIBackpressureError()

    def __exit__(self, *_args: object) -> None:
        self._semaphore.release()


def execute_with_resilience(
    operation: Callable[[float], ResultT],
    budget: ResilienceBudget,
    *,
    monotonic: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
    random_unit: Callable[[], float] = random.random,
) -> ResultT:
    """Execute a pre-classified operation without exceeding its global deadline."""

    started = monotonic()
    last_error: ClassifiedAIError | None = None
    for attempt in range(1, budget.max_attempts + 1):
        remaining = budget.total_timeout_seconds - (monotonic() - started)
        if remaining <= 0:
            break
        try:
            return operation(remaining)
        except ClassifiedAIError as exc:
            last_error = exc
            if not exc.retryable or attempt >= budget.max_attempts:
                raise
            delay = budget.delay(attempt, random_unit())
            if exc.retry_after_seconds is not None:
                delay = min(max(delay, exc.retry_after_seconds), budget.retry_max_seconds)
            remaining = budget.total_timeout_seconds - (monotonic() - started)
            if delay <= 0 or delay >= remaining:
                break
            sleeper(delay)
    raise ClassifiedAIError(
        "AI provider retry budget exhausted",
        FailureClass.EXHAUSTED,
        retryable=False,
    ) from last_error
