"""Replaceable local alert contracts without delivery integrations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Literal, Protocol

from app.core.observability import current_correlation_id

AlertSeverity = Literal["info", "warning", "critical"]
ALERT_EVENT_CODES = frozenset(
    {
        "dependency_unavailable",
        "repeated_auth_failure_threshold",
        "rate_limit_threshold",
        "backup_job_failed",
        "restore_failed",
        "readiness_degraded",
        "ai_provider_unavailable",
        "processing_failure_threshold",
        "unexpected_internal_error",
    }
)
_ALLOWED_CONTEXT = frozenset({"dependency", "operation", "route", "status_class", "scope"})


@dataclass(frozen=True)
class AlertEvent:
    severity: AlertSeverity
    code: str
    correlation_id: str | None
    timestamp: str
    context: dict[str, str]


class AlertProvider(Protocol):
    def send(self, event: AlertEvent) -> None: ...


class NoOpAlertProvider:
    def send(self, event: AlertEvent) -> None:
        return None


class LocalAlertProvider:
    def __init__(self) -> None:
        self.events: list[AlertEvent] = []
        self._lock = RLock()

    def send(self, event: AlertEvent) -> None:
        with self._lock:
            self.events.append(event)

    def reset(self) -> None:
        with self._lock:
            self.events.clear()


class AlertManager:
    def __init__(self, provider: AlertProvider, *, cooldown_seconds: float = 30) -> None:
        self._provider = provider
        self._cooldown_seconds = cooldown_seconds
        self._last_sent: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
        self._lock = RLock()

    def emit(
        self,
        code: str,
        severity: AlertSeverity,
        *,
        context: dict[str, str] | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        if code not in ALERT_EVENT_CODES:
            raise ValueError("Unknown alert event code")
        safe_context = context or {}
        if set(safe_context) - _ALLOWED_CONTEXT:
            raise ValueError("Alert context is outside the allowlist")
        if any(not value or len(value) > 100 for value in safe_context.values()):
            raise ValueError("Alert context value is invalid")
        key = (code, tuple(sorted(safe_context.items())))
        now = time.monotonic()
        with self._lock:
            last = self._last_sent.get(key)
            if last is not None and now - last < self._cooldown_seconds:
                return False
            self._last_sent[key] = now
        event = AlertEvent(
            severity=severity,
            code=code,
            correlation_id=correlation_id or current_correlation_id(),
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            context=dict(safe_context),
        )
        try:
            self._provider.send(event)
        except Exception:
            return False
        return True

    def reset(self) -> None:
        with self._lock:
            self._last_sent.clear()
