"""Local request tracing foundation with no exporter or external transport."""

from __future__ import annotations

import re
import time
from contextlib import AbstractContextManager
from contextvars import ContextVar, Token
from dataclasses import dataclass, replace
from threading import RLock
from typing import Literal, Protocol
from uuid import uuid4

from app.core.observability import current_correlation_id

TraceStatus = Literal["ok", "error"]
_current_span_id: ContextVar[str | None] = ContextVar("span_id", default=None)
_OPERATION = re.compile(r"^[a-z][a-z0-9_.-]{0,79}$")


@dataclass(frozen=True)
class SpanRecord:
    span_id: str
    parent_span_id: str | None
    correlation_id: str | None
    operation: str
    duration_ms: float
    status: TraceStatus
    error_type: str | None


class TraceProvider(Protocol):
    def record(self, span: SpanRecord) -> None: ...


class NoOpTraceProvider:
    def record(self, span: SpanRecord) -> None:
        return None


class LocalTraceProvider:
    def __init__(self) -> None:
        self.spans: list[SpanRecord] = []
        self._lock = RLock()

    def record(self, span: SpanRecord) -> None:
        with self._lock:
            self.spans.append(span)

    def reset(self) -> None:
        with self._lock:
            self.spans.clear()


def current_span_id() -> str | None:
    return _current_span_id.get()


class _SpanScope(AbstractContextManager["_SpanScope"]):
    def __init__(self, provider: TraceProvider, operation: str) -> None:
        if not _OPERATION.fullmatch(operation):
            raise ValueError("Trace operation must be normalized")
        self._provider = provider
        self._operation = operation
        self._parent_span_id = current_span_id()
        self._span_id = uuid4().hex[:16]
        self._started = 0.0
        self._token: Token[str | None] | None = None
        self._status: TraceStatus = "ok"
        self._error_type: str | None = None

    @property
    def span_id(self) -> str:
        return self._span_id

    def set_error(self, error_type: str) -> None:
        self._status = "error"
        self._error_type = error_type[:80]

    def __enter__(self) -> "_SpanScope":
        self._started = time.perf_counter()
        self._token = _current_span_id.set(self._span_id)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.set_error(getattr(exc_type, "__name__", "controlled_error"))
        span = SpanRecord(
            span_id=self._span_id,
            parent_span_id=self._parent_span_id,
            correlation_id=current_correlation_id(),
            operation=self._operation,
            duration_ms=round((time.perf_counter() - self._started) * 1000, 3),
            status=self._status,
            error_type=self._error_type,
        )
        try:
            self._provider.record(replace(span))
        except Exception:
            pass
        if self._token is not None:
            _current_span_id.reset(self._token)
        return None


class Tracer:
    def __init__(self, provider: TraceProvider) -> None:
        self._provider = provider

    def start_span(self, operation: str) -> _SpanScope:
        return _SpanScope(self._provider, operation)
