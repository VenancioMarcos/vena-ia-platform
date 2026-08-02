"""Structured, allowlisted request telemetry with correlation context."""

from __future__ import annotations

import json
import logging
import re
import time
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
    return {name: value for name, value in redacted.items() if name in _ALLOWED_FIELDS}


def emit_structured_event(event: str, level: str = "INFO", **fields: Any) -> None:
    payload = structured_event(event, level, **fields)
    _LOGGER.log(getattr(logging, level.upper(), logging.INFO), json.dumps(payload, sort_keys=True))


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, *, application_version: str, environment: str) -> None:
        super().__init__(app)
        self.application_version = application_version
        self.environment = environment

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
            try:
                response = await call_next(request)
            except Exception as exc:
                error_type = type(exc).__name__
                response = JSONResponse(
                    status_code=500,
                    content={
                        "detail": "Internal server error",
                        "request_id": request_id,
                        "correlation_id": correlation_id,
                    },
                )
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            route = request.scope.get("route")
            route_path = getattr(route, "path", "unmatched")
            emit_structured_event(
                "http.request.completed",
                "ERROR" if response.status_code >= 500 else "INFO",
                method=request.method,
                route=route_path,
                status_http=response.status_code,
                duration_ms=round((time.perf_counter() - started) * 1000, 3),
                application_version=self.application_version,
                environment=self.environment,
                error_type=error_type,
            )
            return response
        finally:
            _request_id.reset(request_token)
            _correlation_id.reset(correlation_token)
