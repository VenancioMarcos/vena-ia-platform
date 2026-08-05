import json
import logging
import time
from uuid import UUID, uuid4

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.core.observability import (
    CORRELATION_ID_HEADER,
    LOG_SCHEMA_VERSION,
    REQUEST_ID_HEADER,
    current_correlation_id,
    current_request_id,
    redact_sensitive,
)
from app.main import app, create_app


class FakeReadinessChecker:
    def __init__(self, statuses: dict[str, str]) -> None:
        self.statuses = statuses

    def check(self) -> dict[str, str]:
        return self.statuses


def _uuid(value: str) -> str:
    return str(UUID(value))


def test_request_and_correlation_ids_are_created_and_returned(client: TestClient) -> None:
    response = client.get("/health")

    assert _uuid(response.headers[REQUEST_ID_HEADER])
    assert _uuid(response.headers[CORRELATION_ID_HEADER])


def test_valid_ids_are_preserved_and_propagated_to_request_context() -> None:
    isolated: FastAPI = create_app()

    @isolated.get("/_observability/context")
    def context() -> dict[str, str | None]:
        return {
            "request_id": current_request_id(),
            "correlation_id": current_correlation_id(),
        }

    request_id = str(uuid4())
    correlation_id = str(uuid4())
    response = TestClient(isolated).get(
        "/_observability/context",
        headers={REQUEST_ID_HEADER: request_id, CORRELATION_ID_HEADER: correlation_id},
    )
    assert response.status_code == 200
    assert response.json() == {"request_id": request_id, "correlation_id": correlation_id}
    assert response.headers[REQUEST_ID_HEADER] == request_id
    assert response.headers[CORRELATION_ID_HEADER] == correlation_id


def test_invalid_identifiers_are_replaced(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={REQUEST_ID_HEADER: "../../invalid", CORRELATION_ID_HEADER: "secret-token"},
    )
    assert response.headers[REQUEST_ID_HEADER] != "../../invalid"
    assert response.headers[CORRELATION_ID_HEADER] != "secret-token"
    assert _uuid(response.headers[REQUEST_ID_HEADER])
    assert _uuid(response.headers[CORRELATION_ID_HEADER])


def test_structured_log_is_stable_allowlisted_and_does_not_capture_payload(
    client: TestClient,
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger="vena_ia.observability")
    secret = "Bearer highly-sensitive-token"
    prompt = "private document prompt content"
    response = client.post(
        "/auth/login",
        headers={"Authorization": secret, "Cookie": "session=private"},
        json={"email": "nobody@example.test", "password": prompt},
    )
    assert response.status_code in {401, 422, 503}
    payload = json.loads(caplog.records[-1].message)
    assert payload["schema_version"] == LOG_SCHEMA_VERSION
    assert payload["event"] == "http.request.completed"
    assert payload["route"] == "/auth/login"
    assert payload["status_http"] == response.status_code
    serialized = json.dumps(payload)
    assert secret not in serialized
    assert prompt not in serialized
    assert "Authorization" not in serialized
    assert "Cookie" not in serialized


def test_redaction_covers_tokens_cookies_passwords_secrets_and_ai_content() -> None:
    value = redact_sensitive(
        {
            "Authorization": "Bearer token",
            "Cookie": "session=value",
            "password": "password",
            "api_secret": "secret",
            "document_content": "document",
            "prompt": "question",
            "response": "answer",
            "embedding": [0.1],
            "safe": "visible",
        }
    )
    assert value["safe"] == "visible"
    assert all(value[name] == "[REDACTED]" for name in value if name != "safe")


def test_unhandled_error_is_generic_and_correlated() -> None:
    isolated = create_app()

    @isolated.get("/_observability/failure")
    def failure() -> None:
        raise RuntimeError("password=must-never-reach-response")

    response = TestClient(isolated, raise_server_exceptions=False).get("/_observability/failure")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert response.json()["request_id"] == response.headers[REQUEST_ID_HEADER]
    assert response.json()["correlation_id"] == response.headers[CORRELATION_ID_HEADER]
    assert "password" not in response.text
    assert "Traceback" not in response.text


def test_readiness_reports_healthy_and_unavailable_dependencies(client: TestClient) -> None:
    original = app.state.readiness_checker
    try:
        app.state.readiness_checker = FakeReadinessChecker(
            {"postgresql": "ready", "redis": "ready", "minio": "ready"}
        )
        healthy = client.get("/ready")
        assert healthy.status_code == 200
        assert healthy.json()["status"] == "ready"
        assert healthy.json()["version"] == "1.5.0-dev"

        app.state.readiness_checker = FakeReadinessChecker(
            {"postgresql": "ready", "redis": "unavailable", "minio": "ready"}
        )
        unavailable = client.get("/ready")
        assert unavailable.status_code == 503
        assert unavailable.json()["status"] == "degraded"
        assert unavailable.json()["dependencies"]["redis"] == "unavailable"
        assert "redis://" not in unavailable.text
    finally:
        app.state.readiness_checker = original


def test_observability_middleware_overhead_is_bounded(client: TestClient) -> None:
    started = time.perf_counter()
    for _ in range(30):
        assert client.get("/health").status_code == 200
    average_ms = (time.perf_counter() - started) * 1000 / 30
    assert average_ms < 100
