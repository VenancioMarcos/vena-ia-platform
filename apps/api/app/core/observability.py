"""Structured, allowlisted request telemetry with correlation context."""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

LOG_SCHEMA_VERSION = "vena-ia.observability/v1"
REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
_LOGGER = logging.getLogger("vena_ia.observability")
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_SENSITIVE_KEY = re.compile(
    r"authorization|cookie|token|password|secret|key|prompt|embedding|document|response|content",
    re.IGNORECASE,
)
_ALLOWED_FIELDS = {
    "timestamp",
    "level",
    "event",
    "schema_version",
    "request_id",
    "correlation_id",
    "method",
    "route",
    "status_http",
    "duration_ms",
    "application_version",
    "environment",
    "error_type",
    "dependency",
    "dependency_status",
    "job_id",
    "job_type",
    "job_status",
    "progress",
}


def _safe_identifier(value: str | None) -> str:
    if value:
        try:
            return str(UUID(value))
        except ValueError:
            pass
    return str(uuid4())


def current_request_id() -> str | None:
    return _request_id.get()


def current_correlation_id() -> str | None:
    return _correlation_id.get()


@contextmanager
def observability_context(
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> Generator[tuple[str, str], None, None]:
    """Create the same validated correlation scope used by HTTP middleware."""
    safe_request_id = _safe_identifier(request_id)
    safe_correlation_id = _safe_identifier(correlation_id)
    request_token = _request_id.set(safe_request_id)
    correlation_token = _correlation_id.set(safe_correlation_id)
    try:
        yield safe_request_id, safe_correlation_id
    finally:
        _request_id.reset(request_token)
        _correlation_id.reset(correlation_token)


def redact_sensitive(value: Any, *, key: str = "") -> Any:
    """Defense-in-depth redaction for values before allowlist filtering."""
    if _SENSITIVE_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {name: redact_sensitive(item, key=str(name)) for name, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_sensitive(item, key=key) for item in value]
    return value


def structured_event(event: str, level: str = "INFO", **fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level.upper(),
        "event": event,
        "schema_version": LOG_SCHEMA_VERSION,
        "request_id": current_request_id(),
        "correlation_id": current_correlation_id(),
    }
    base.update(fields)
    redacted = redact_sensitive(base)
    if "job_id" in redacted:
        redacted["job_id"] = _safe_identifier(redacted["job_id"])
    return {name: value for name, value in redacted.items() if name in _ALLOWED_FIELDS}


def emit_structured_event(event: str, level: str = "INFO", **fields: Any) -> None:
    payload = structured_event(event, level, **fields)
    _LOGGER.log(getattr(logging, level.upper(), logging.INFO), json.dumps(payload, sort_keys=True))


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        *,
        application_version: str,
        environment: str,
        metric_collector: Any,
        tracer: Any,
        alert_manager: Any,
    ) -> None:
        super().__init__(app)
        self.application_version = application_version
        self.environment = environment
        self.metric_collector = metric_collector
        self.tracer = tracer
        self.alert_manager = alert_manager

    @staticmethod
    def _safe(operation: Any, *args: Any, **kwargs: Any) -> None:
        try:
            operation(*args, **kwargs)
        except Exception:
            pass

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _safe_identifier(request.headers.get(REQUEST_ID_HEADER))
        correlation_id = _safe_identifier(request.headers.get(CORRELATION_ID_HEADER))
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request_token: Token[str | None] = _request_id.set(request_id)
        correlation_token: Token[str | None] = _correlation_id.set(correlation_id)
        started = time.perf_counter()
        error_type: str | None = None
        try:
            with self.tracer.start_span("http.request") as span:
                try:
                    response = await call_next(request)
                except Exception as exc:
                    error_type = type(exc).__name__
                    span.set_error(error_type)
                    response = JSONResponse(
                        status_code=500,
                        content={
                            "detail": "Internal server error",
                            "request_id": request_id,
                            "correlation_id": correlation_id,
                        },
                    )
                if response.status_code >= 500 and error_type is None:
                    span.set_error("http_5xx")
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            route = request.scope.get("route")
            route_path = getattr(route, "path", "unmatched")
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            status_class = f"{response.status_code // 100}xx"
            emit_structured_event(
                "http.request.completed",
                "ERROR" if response.status_code >= 500 else "INFO",
                method=request.method,
                route=route_path,
                status_http=response.status_code,
                duration_ms=duration_ms,
                application_version=self.application_version,
                environment=self.environment,
                error_type=error_type,
            )
            request_labels = {
                "method": request.method,
                "route": route_path,
                "status_class": status_class,
            }
            self._safe(
                self.metric_collector.increment,
                "http_requests_total",
                request_labels,
            )
            self._safe(
                self.metric_collector.observe,
                "http_request_duration_ms",
                request_labels,
                duration_ms,
            )
            if response.status_code >= 500:
                self._safe(
                    self.metric_collector.increment,
                    "http_internal_errors_total",
                    {"route": route_path},
                )
                if response.status_code == 500:
                    self._safe(
                        self.alert_manager.emit,
                        "unexpected_internal_error",
                        "critical",
                        context={"route": route_path, "status_class": status_class},
                        correlation_id=correlation_id,
                    )
            if response.status_code == 429:
                scope = "authentication" if route_path.startswith(("/auth", "/users")) else "api"
                self._safe(
                    self.metric_collector.increment,
                    "rate_limits_total",
                    {"scope": scope},
                )
                self._safe(
                    self.alert_manager.emit,
                    "rate_limit_threshold",
                    "warning",
                    context={"scope": scope},
                    correlation_id=correlation_id,
                )
            if response.status_code == 401 and route_path == "/auth/login":
                self._safe(
                    self.alert_manager.emit,
                    "repeated_auth_failure_threshold",
                    "warning",
                    context={"scope": "authentication"},
                    correlation_id=correlation_id,
                )
            if response.status_code in {502, 503} and (
                route_path.startswith("/ai/")
                or route_path.endswith("/knowledge/ask")
                or route_path.endswith("/embeddings")
                or route_path.endswith("/ask")
            ):
                self._safe(
                    self.metric_collector.increment,
                    "ai_provider_failures_total",
                    {"operation": "ai.request"},
                )
                self._safe(
                    self.alert_manager.emit,
                    "ai_provider_unavailable",
                    "critical",
                    context={"operation": "ai.request"},
                    correlation_id=correlation_id,
                )
            processing_routes = {
                "/documents/{document_id}/process",
                "/documents/{document_id}/processing",
                "/documents/{document_id}/embeddings",
            }
            if route_path in processing_routes:
                outcome = "completed" if response.status_code < 400 else "failed"
                self._safe(
                    self.metric_collector.increment,
                    "processing_jobs_total",
                    {"operation": "document.processing", "outcome": outcome},
                )
                if outcome == "failed":
                    self._safe(
                        self.alert_manager.emit,
                        "processing_failure_threshold",
                        "warning",
                        context={"operation": "document.processing"},
                        correlation_id=correlation_id,
                    )
            return response
        finally:
            _request_id.reset(request_token)
            _correlation_id.reset(correlation_token)
