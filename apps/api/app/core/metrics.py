"""Bounded, in-process metrics contract with no external exporter."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Literal, Protocol

METRICS_SCHEMA_VERSION = "vena-ia.metrics/v1"
MetricKind = Literal["counter", "gauge", "histogram"]


@dataclass(frozen=True)
class MetricSpec:
    name: str
    kind: MetricKind
    labels: tuple[str, ...]
    unit: str
    buckets: tuple[float, ...] = ()


METRIC_SPECS: dict[str, MetricSpec] = {
    "http_requests_total": MetricSpec(
        "http_requests_total", "counter", ("method", "route", "status_class"), "requests"
    ),
    "http_request_duration_ms": MetricSpec(
        "http_request_duration_ms",
        "histogram",
        ("method", "route", "status_class"),
        "milliseconds",
        (5, 10, 25, 50, 100, 250, 500, 1_000, 2_500, 5_000),
    ),
    "http_internal_errors_total": MetricSpec(
        "http_internal_errors_total", "counter", ("route",), "errors"
    ),
    "readiness_state": MetricSpec("readiness_state", "gauge", ("dependency",), "state"),
    "dependency_failures_total": MetricSpec(
        "dependency_failures_total", "counter", ("dependency",), "failures"
    ),
    "ai_provider_failures_total": MetricSpec(
        "ai_provider_failures_total", "counter", ("operation",), "failures"
    ),
    "processing_jobs_total": MetricSpec(
        "processing_jobs_total", "counter", ("operation", "outcome"), "jobs"
    ),
    "retry_attempts_total": MetricSpec(
        "retry_attempts_total", "counter", ("operation",), "attempts"
    ),
    "async_jobs_total": MetricSpec(
        "async_jobs_total", "counter", ("job_type", "job_status"), "jobs"
    ),
    "async_job_duration_ms": MetricSpec(
        "async_job_duration_ms",
        "histogram",
        ("job_type", "job_status"),
        "milliseconds",
        (10, 50, 100, 250, 500, 1_000, 5_000, 30_000, 60_000, 300_000),
    ),
    "job_queue_recoveries_total": MetricSpec(
        "job_queue_recoveries_total", "counter", (), "jobs"
    ),
    "rate_limits_total": MetricSpec(
        "rate_limits_total", "counter", ("scope",), "limits"
    ),
    "resilience_attempts_total": MetricSpec(
        "resilience_attempts_total", "counter", ("operation", "attempt_class"), "attempts"
    ),
    "resilience_failures_total": MetricSpec(
        "resilience_failures_total", "counter", ("dependency", "error_class"), "failures"
    ),
    "backpressure_rejections_total": MetricSpec(
        "backpressure_rejections_total", "counter", ("operation",), "rejections"
    ),
    "concurrency_in_use": MetricSpec(
        "concurrency_in_use", "gauge", ("operation",), "operations"
    ),
    "concurrency_limit": MetricSpec(
        "concurrency_limit", "gauge", ("operation",), "operations"
    ),
    "resilience_operation_duration_ms": MetricSpec(
        "resilience_operation_duration_ms",
        "histogram",
        ("operation", "outcome"),
        "milliseconds",
        (1, 5, 10, 25, 50, 100, 250, 500, 1_000, 5_000, 30_000),
    ),
    "requests_in_flight": MetricSpec(
        "requests_in_flight", "gauge", ("operation",), "requests"
    ),
    "requests_rejected_total": MetricSpec(
        "requests_rejected_total", "counter", ("operation",), "requests"
    ),
    "queue_depth": MetricSpec("queue_depth", "gauge", ("operation",), "jobs"),
    "jobs_in_flight": MetricSpec(
        "jobs_in_flight", "gauge", ("job_type",), "jobs"
    ),
    "worker_utilization": MetricSpec(
        "worker_utilization", "gauge", ("job_type",), "ratio"
    ),
    "dependency_concurrency": MetricSpec(
        "dependency_concurrency", "gauge", ("dependency", "operation"), "operations"
    ),
    "recovery_after_saturation_total": MetricSpec(
        "recovery_after_saturation_total", "counter", ("operation",), "recoveries"
    ),
    "e2e_duration_ms": MetricSpec(
        "e2e_duration_ms", "histogram", ("outcome",), "milliseconds",
        (100, 250, 500, 1_000, 2_500, 5_000, 10_000, 30_000),
    ),
    "soak_errors_total": MetricSpec(
        "soak_errors_total", "counter", ("operation",), "errors"
    ),
}

PROHIBITED_LABELS = frozenset(
    {
        "user_id",
        "project_id",
        "document_id",
        "token",
        "cookie",
        "password",
        "secret",
        "key",
        "query",
        "body",
        "prompt",
        "response",
        "embedding",
    }
)
_ALLOWED_LABEL_VALUES = {
    "method": frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}),
    "status_class": frozenset({"1xx", "2xx", "3xx", "4xx", "5xx"}),
    "dependency": frozenset({"postgresql", "redis", "minio", "worker", "openai", "api"}),
    "operation": frozenset({"ai.request", "document.processing", "backup", "restore"}),
    "outcome": frozenset({"started", "completed", "failed"}),
    "attempt_class": frozenset({"initial", "retry", "recovered", "exhausted"}),
    "error_class": frozenset(
        {
            "connect_timeout", "read_timeout", "total_timeout", "connection_refused",
            "resolution", "authentication", "authorization", "rate_limit",
            "temporary_unavailable", "permanent", "invalid_payload", "invalid_response",
            "conflict", "not_found", "cancelled", "exhausted", "internal",
        }
    ),
    "scope": frozenset({"authentication", "api"}),
    "job_type": frozenset({"document.processing"}),
    "job_status": frozenset(
        {
            "queued",
            "running",
            "succeeded",
            "failed",
            "retry_scheduled",
            "cancellation_requested",
            "cancelled",
            "timed_out",
        }
    ),
}


class MetricCollector(Protocol):
    def increment(self, name: str, labels: dict[str, str], value: float = 1) -> None: ...

    def observe(self, name: str, labels: dict[str, str], value: float) -> None: ...

    def set_gauge(self, name: str, labels: dict[str, str], value: float) -> None: ...

    def snapshot(self) -> dict[str, object]: ...

    def reset(self) -> None: ...


def _validated_key(name: str, labels: dict[str, str], kind: MetricKind) -> tuple[str, ...]:
    spec = METRIC_SPECS.get(name)
    if spec is None or spec.kind != kind:
        raise ValueError("Unknown metric or invalid metric operation")
    if set(labels) & PROHIBITED_LABELS or set(labels) != set(spec.labels):
        raise ValueError("Metric labels do not match the bounded contract")
    values: list[str] = []
    for label in spec.labels:
        value = labels[label]
        if not value or len(value) > 100 or "?" in value or "\n" in value:
            raise ValueError("Metric label value is invalid")
        allowed_values = _ALLOWED_LABEL_VALUES.get(label)
        if allowed_values is not None and value not in allowed_values:
            raise ValueError("Metric label value is outside the bounded contract")
        if label == "route" and not value.startswith("/") and value != "unmatched":
            raise ValueError("Route labels must use normalized API templates")
        if label == "route" and any(
            segment.isdigit() or len(segment) == 36
            for segment in value.split("/")
            if segment and not (segment.startswith("{") and segment.endswith("}"))
        ):
            raise ValueError("Route labels must not contain dynamic identifiers")
        values.append(value)
    return tuple(values)


class InMemoryMetricCollector:
    """Thread-safe local collector intended for one process and deterministic tests."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._counters: dict[tuple[str, tuple[str, ...]], float] = {}
        self._gauges: dict[tuple[str, tuple[str, ...]], float] = {}
        self._histograms: dict[tuple[str, tuple[str, ...]], list[float]] = {}

    def increment(self, name: str, labels: dict[str, str], value: float = 1) -> None:
        if value < 0:
            raise ValueError("Counters cannot decrease")
        key = (name, _validated_key(name, labels, "counter"))
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def observe(self, name: str, labels: dict[str, str], value: float) -> None:
        if value < 0:
            raise ValueError("Histogram observations cannot be negative")
        key = (name, _validated_key(name, labels, "histogram"))
        with self._lock:
            self._histograms.setdefault(key, []).append(value)

    def set_gauge(self, name: str, labels: dict[str, str], value: float) -> None:
        key = (name, _validated_key(name, labels, "gauge"))
        with self._lock:
            self._gauges[key] = value

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            series: list[dict[str, object]] = []
            for (name, values), value in sorted(self._counters.items()):
                spec = METRIC_SPECS[name]
                series.append(self._series(spec, values, {"value": value}))
            for (name, values), value in sorted(self._gauges.items()):
                spec = METRIC_SPECS[name]
                series.append(self._series(spec, values, {"value": value}))
            for (name, values), observations in sorted(self._histograms.items()):
                spec = METRIC_SPECS[name]
                counts = [sum(item <= bucket for item in observations) for bucket in spec.buckets]
                series.append(
                    self._series(
                        spec,
                        values,
                        {
                            "count": len(observations),
                            "sum": round(sum(observations), 6),
                            "buckets": [
                                {"le": bucket, "count": count}
                                for bucket, count in zip(spec.buckets, counts, strict=True)
                            ],
                        },
                    )
                )
            return {"schema_version": METRICS_SCHEMA_VERSION, "series": series}

    @staticmethod
    def _series(
        spec: MetricSpec, values: tuple[str, ...], measurements: dict[str, object]
    ) -> dict[str, object]:
        return {
            "name": spec.name,
            "type": spec.kind,
            "unit": spec.unit,
            "labels": dict(zip(spec.labels, values, strict=True)),
            **measurements,
        }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


class NoOpMetricCollector:
    def increment(self, name: str, labels: dict[str, str], value: float = 1) -> None:
        return None

    def observe(self, name: str, labels: dict[str, str], value: float) -> None:
        return None

    def set_gauge(self, name: str, labels: dict[str, str], value: float) -> None:
        return None

    def snapshot(self) -> dict[str, object]:
        return {"schema_version": METRICS_SCHEMA_VERSION, "series": []}

    def reset(self) -> None:
        return None


def safe_metric_call(operation: object, *args: object, **kwargs: object) -> None:
    """Invoke collector methods fail-open so telemetry never breaks product work."""
    try:
        if callable(operation):
            operation(*args, **kwargs)
    except Exception:
        return None
