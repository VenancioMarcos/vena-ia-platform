"""Process-local fixed-window rate limiting primitives.

This is the first application-layer control for public authentication routes. It
does not replace a distributed limiter or trusted gateway for horizontal
production deployments.
"""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic


@dataclass
class _Window:
    count: int
    resets_at: float


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Rate limit exceeded")
        self.retry_after_seconds = retry_after_seconds


class FixedWindowRateLimiter:
    """Thread-safe in-process limiter with an injectable monotonic clock."""

    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._windows: dict[str, _Window] = {}
        self._lock = Lock()

    def consume(self, key: str, *, limit: int, window_seconds: int) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("Rate limit and window must be positive")

        now = self._clock()
        with self._lock:
            window = self._windows.get(key)
            if window is None or window.resets_at <= now:
                self._windows[key] = _Window(
                    count=1,
                    resets_at=now + window_seconds,
                )
                return

            if window.count >= limit:
                raise RateLimitExceeded(max(1, ceil(window.resets_at - now)))

            window.count += 1

    def clear(self) -> None:
        with self._lock:
            self._windows.clear()
