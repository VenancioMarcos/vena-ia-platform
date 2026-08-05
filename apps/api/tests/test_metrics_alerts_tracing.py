import time

import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from app.core.alerts import AlertManager, LocalAlertProvider, NoOpAlertProvider
from app.core.config import settings
from app.core.metrics import InMemoryMetricCollector, METRICS_SCHEMA_VERSION
from app.core.observability import CORRELATION_ID_HEADER, REQUEST_ID_HEADER
from app.core.tracing import LocalTraceProvider, Tracer, current_span_id
from app.main import app, create_app
from app.modules.audit.models import SecurityAuditEvent


def _series(snapshot: dict[str, object], name: str) -> list[dict[str, object]]:
    return [item for item in snapshot["series"] if item["name"] == name]  # type: ignore[index]


def test_request_metrics_have_bounded_route_method_class_and_duration(client) -> None:
    response = client.get("/health?project_id=secret")
    assert response.status_code == 200
    snapshot = app.state.metric_collector.snapshot()
    requests = _series(snapshot, "http_requests_total")
    durations = _series(snapshot, "http_request_duration_ms")
    assert snapshot["schema_version"] == METRICS_SCHEMA_VERSION
    assert any(
        item["labels"] == {"method": "GET", "route": "/health", "status_class": "2xx"}
        for item in requests
    )
    assert durations and durations[-1]["count"] >= 1
    assert "secret" not in str(snapshot)


def test_readiness_metrics_and_dependency_failure_are_recorded(client) -> None:
    original = app.state.readiness_checker

    class Degraded:
        def check(self) -> dict[str, str]:
            return {"postgresql": "ready", "redis": "unavailable", "minio": "ready"}

    try:
        app.state.readiness_checker = Degraded()
        response = client.get("/ready")
    finally:
        app.state.readiness_checker = original
    assert response.status_code == 503
    snapshot = app.state.metric_collector.snapshot()
    failures = _series(snapshot, "dependency_failures_total")
    assert any(item["labels"] == {"dependency": "redis"} for item in failures)


def test_metric_contract_rejects_forbidden_and_unbounded_labels() -> None:
    collector = InMemoryMetricCollector()
    with pytest.raises(ValueError):
        collector.increment("http_requests_total", {"user_id": "member"})
    with pytest.raises(ValueError):
        collector.increment(
            "http_requests_total",
            {"method": "GET", "route": "/projects/123?token=x", "status_class": "2xx"},
        )
    with pytest.raises(ValueError):
        collector.increment("arbitrary_event", {})


def test_disabled_collection_and_broken_collector_do_not_break_api(monkeypatch) -> None:
    monkeypatch.setattr(settings, "observability_collection_enabled", False)
    isolated = create_app()
    assert TestClient(isolated).get("/health").status_code == 200
    assert isolated.state.metric_collector.snapshot()["series"] == []

    class BrokenCollector:
        def increment(self, *args, **kwargs) -> None:
            raise RuntimeError("collector unavailable")

        observe = increment
        set_gauge = increment

        def snapshot(self) -> dict[str, object]:
            raise RuntimeError("collector unavailable")

    monkeypatch.setattr(settings, "observability_collection_enabled", True)
    monkeypatch.setattr("app.main.InMemoryMetricCollector", BrokenCollector)
    broken = create_app()
    assert TestClient(broken).get("/health").status_code == 200


def test_metrics_endpoint_is_disabled_by_default_and_admin_protected(
    client, make_account, monkeypatch
) -> None:
    admin = make_account("metrics-admin@vena-ia.dev", role="admin")
    member = make_account("metrics-member@vena-ia.dev")
    assert client.get("/internal/metrics", headers=admin.headers).status_code == 404
    monkeypatch.setattr(settings, "observability_metrics_endpoint_enabled", True)
    assert client.get("/internal/metrics").status_code == 401
    assert client.get("/internal/metrics", headers=member.headers).status_code == 403
    allowed = client.get("/internal/metrics", headers=admin.headers)
    assert allowed.status_code == 200
    assert allowed.json()["schema_version"] == METRICS_SCHEMA_VERSION
    assert "access_token" not in allowed.text


def test_rate_limit_and_ai_failure_metrics_are_aggregated(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_login_rate_limit_requests", 1)
    client.post("/auth/login", json={"email": "none@test.dev", "password": "wrong-password"})
    limited = client.post(
        "/auth/login", json={"email": "none@test.dev", "password": "wrong-password"}
    )
    assert limited.status_code == 429
    assert _series(app.state.metric_collector.snapshot(), "rate_limits_total")


def test_local_alert_contract_severity_cooldown_and_no_external_delivery() -> None:
    provider = LocalAlertProvider()
    manager = AlertManager(provider, cooldown_seconds=60)
    assert manager.emit(
        "dependency_unavailable", "critical", context={"dependency": "redis"}
    )
    assert not manager.emit(
        "dependency_unavailable", "critical", context={"dependency": "redis"}
    )
    assert provider.events[0].severity == "critical"
    assert provider.events[0].context == {"dependency": "redis"}
    assert AlertManager(NoOpAlertProvider(), cooldown_seconds=0).emit(
        "backup_job_failed", "critical", context={"operation": "backup"}
    )


def test_alert_threshold_is_bounded_resettable_and_precedes_cooldown() -> None:
    provider = LocalAlertProvider()
    manager = AlertManager(
        provider,
        cooldown_seconds=0,
        thresholds={"processing_failure_threshold": 3},
    )
    context = {"operation": "document.processing"}
    assert not manager.emit("processing_failure_threshold", "warning", context=context)
    assert not manager.emit("processing_failure_threshold", "warning", context=context)
    assert manager.emit("processing_failure_threshold", "warning", context=context)
    assert len(provider.events) == 1
    manager.reset()
    assert not manager.emit("processing_failure_threshold", "warning", context=context)
    with pytest.raises(ValueError, match="thresholds"):
        AlertManager(provider, thresholds={"unknown": 1})


def test_alert_contract_rejects_sensitive_context() -> None:
    manager = AlertManager(NoOpAlertProvider())
    with pytest.raises(ValueError):
        manager.emit("restore_failed", "critical", context={"token": "secret"})


def test_local_tracing_parent_child_duration_error_and_context_cleanup() -> None:
    provider = LocalTraceProvider()
    tracer = Tracer(provider)
    with tracer.start_span("request") as parent:
        assert current_span_id() == parent.span_id
        with tracer.start_span("database.query") as child:
            time.sleep(0.001)
            child.set_error("controlled_error")
    assert current_span_id() is None
    assert len(provider.spans) == 2
    child_record, parent_record = provider.spans
    assert child_record.parent_span_id == parent_record.span_id
    assert child_record.status == "error"
    assert child_record.duration_ms >= 0


def test_combined_local_observability_overhead_is_bounded(monkeypatch) -> None:
    provider = LocalTraceProvider()
    monkeypatch.setattr("app.main.NoOpTraceProvider", lambda: provider)
    isolated = create_app()
    client = TestClient(isolated)
    started = time.perf_counter()
    for _ in range(30):
        assert client.get("/health").status_code == 200
    average_ms = (time.perf_counter() - started) * 1000 / 30
    assert average_ms < 100
    assert len(provider.spans) == 30
    assert all(span.operation == "http.request" for span in provider.spans)


def test_authentication_and_project_audit_events_persist_correlation(
    client, db_session, make_account
) -> None:
    account = make_account("correlated-audit@vena-ia.dev")
    response = client.post(
        "/projects",
        headers={
            **account.headers,
            REQUEST_ID_HEADER: "11111111-1111-4111-8111-111111111111",
            CORRELATION_ID_HEADER: "22222222-2222-4222-8222-222222222222",
        },
        json={"name": "Correlated", "status": "ACTIVE"},
    )
    assert response.status_code == 201
    db_session.expire_all()
    event = db_session.scalar(
        select(SecurityAuditEvent).where(SecurityAuditEvent.event_type == "PROJECT_CREATED")
    )
    assert event is not None
    assert event.request_id == "11111111-1111-4111-8111-111111111111"
    assert event.correlation_id == "22222222-2222-4222-8222-222222222222"
    serialized = str(event.__dict__)
    assert "Bearer " not in serialized
    assert "Correlated" not in serialized

    login_request_id = "33333333-3333-4333-8333-333333333333"
    login_correlation_id = "44444444-4444-4444-8444-444444444444"
    login = client.post(
        "/auth/login",
        headers={
            REQUEST_ID_HEADER: login_request_id,
            CORRELATION_ID_HEADER: login_correlation_id,
        },
        json={"email": account.email, "password": "correct-horse-battery-staple"},
    )
    assert login.status_code == 200
    db_session.expire_all()
    auth_event = db_session.scalar(
        select(SecurityAuditEvent).where(SecurityAuditEvent.request_id == login_request_id)
    )
    assert auth_event is not None
    assert auth_event.event_type == "LOGIN_SUCCESS"
    assert auth_event.correlation_id == login_correlation_id
