from sqlalchemy import select

from app.core.config import settings
from app.modules.audit.models import SecurityAuditEvent
from app.modules.auth.tokens import create_access_token
from app.modules.auth.security_store import SecurityStoreUnavailable
from app.modules.users.models import User

NEW_PASSWORD = "new-legacy-password-safe"


def _event_types(db_session) -> list[str]:
    db_session.expire_all()
    return list(
        db_session.scalars(
            select(SecurityAuditEvent.event_type).order_by(
                SecurityAuditEvent.occurred_at,
                SecurityAuditEvent.id,
            )
        )
    )


def _legacy_user(db_session, email: str = "legacy@vena-ia.dev") -> User:
    user = User(
        name="Legacy User",
        email=email,
        role="member",
        password_hash=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success_and_failure_are_audited(client, db_session) -> None:
    client.post(
        "/auth/register",
        json={
            "name": "Audited User",
            "email": "audited-login@vena-ia.dev",
            "password": "correct-horse-battery-staple",
        },
    )
    success = client.post(
        "/auth/login",
        json={
            "email": "audited-login@vena-ia.dev",
            "password": "correct-horse-battery-staple",
        },
    )
    failure = client.post(
        "/auth/login",
        json={"email": "audited-login@vena-ia.dev", "password": "wrong-password"},
    )

    assert success.status_code == 200
    assert failure.status_code == 401
    assert "LOGIN_SUCCESS" in _event_types(db_session)
    assert "LOGIN_FAILURE" in _event_types(db_session)


def test_rate_limit_logout_and_rejected_token_are_audited(
    client, db_session, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "auth_login_rate_limit_requests", 1)
    client.post(
        "/auth/login",
        json={"email": "missing@vena-ia.dev", "password": "wrong-password"},
    )
    limited = client.post(
        "/auth/login",
        json={"email": "missing@vena-ia.dev", "password": "wrong-password"},
    )
    logout = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert limited.status_code == 429
    assert logout.status_code == 204
    event_types = _event_types(db_session)
    assert "RATE_LIMIT_EXCEEDED" in event_types
    assert "TOKEN_REJECTED" in event_types
    assert "LOGOUT" in event_types


def test_admin_sets_legacy_credential_and_invalidates_old_session(
    client, db_session, make_account
) -> None:
    admin = make_account("audit-admin@vena-ia.dev", role="admin")
    legacy = _legacy_user(db_session)
    old_token, _ = create_access_token(
        legacy.id,
        settings.auth_secret_key,
        settings.auth_token_expiration_minutes,
        auth_version=legacy.auth_version,
    )

    response = client.put(
        f"/users/{legacy.id}/credentials",
        headers=admin.headers,
        json={"password": NEW_PASSWORD},
    )
    old_session = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {old_token}"}
    )
    login = client.post(
        "/auth/login",
        json={"email": legacy.email, "password": NEW_PASSWORD},
    )

    assert response.status_code == 200
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    assert response.json()["role"] == "member"
    assert old_session.status_code == 401
    assert login.status_code == 200
    db_session.refresh(legacy)
    assert legacy.password_hash is not None
    assert legacy.auth_version == 1
    assert "LEGACY_CREDENTIAL_SET" in _event_types(db_session)


def test_legacy_credential_controls_and_denials_are_audited(
    client, db_session, make_account
) -> None:
    admin = make_account("controls-admin@vena-ia.dev", role="admin")
    member = make_account("controls-member@vena-ia.dev")
    legacy = _legacy_user(db_session, "controlled-legacy@vena-ia.dev")

    forbidden = client.put(
        f"/users/{legacy.id}/credentials",
        headers=member.headers,
        json={"password": NEW_PASSWORD},
    )
    self_reset = client.put(
        f"/users/{admin.id}/credentials",
        headers=admin.headers,
        json={"password": NEW_PASSWORD},
    )
    missing = client.put(
        "/users/00000000-0000-0000-0000-000000000000/credentials",
        headers=admin.headers,
        json={"password": NEW_PASSWORD},
    )
    invalid = client.put(
        f"/users/{legacy.id}/credentials",
        headers=admin.headers,
        json={"password": "short"},
    )
    existing = client.put(
        f"/users/{member.id}/credentials",
        headers=admin.headers,
        json={"password": NEW_PASSWORD},
    )

    assert forbidden.status_code == 403
    assert self_reset.status_code == 403
    assert missing.status_code == 404
    assert invalid.status_code == 422
    assert existing.status_code == 409
    event_types = _event_types(db_session)
    assert "ADMIN_OPERATION_DENIED" in event_types
    assert "LEGACY_CREDENTIAL_RESET_DENIED" in event_types


def test_audit_query_is_admin_only_filtered_and_paginated(
    client, db_session, make_account
) -> None:
    admin = make_account("query-admin@vena-ia.dev", role="admin")
    member = make_account("query-member@vena-ia.dev")

    forbidden = client.get("/audit/security-events", headers=member.headers)
    listed = client.get(
        "/audit/security-events?event_type=LOGIN_SUCCESS&offset=0&limit=1",
        headers=admin.headers,
    )

    assert forbidden.status_code == 403
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    event = listed.json()[0]
    assert event["event_type"] == "LOGIN_SUCCESS"
    assert set(event) == {
        "id",
        "event_type",
        "occurred_at",
        "actor_user_id",
        "target_user_id",
        "outcome",
        "reason",
        "origin",
        "request_id",
        "correlation_id",
    }
    serialized = str(listed.json())
    assert "correct-horse-battery-staple" not in serialized
    assert "password_hash" not in serialized
    assert "access_token" not in serialized
    assert "ADMIN_OPERATION_DENIED" in _event_types(db_session)


class UnavailableSecurityStore:
    def consume(self, *args, **kwargs) -> None:
        raise SecurityStoreUnavailable

    def revoke(self, *args, **kwargs) -> None:
        raise SecurityStoreUnavailable

    def contains(self, *args, **kwargs) -> bool:
        raise SecurityStoreUnavailable


def test_security_store_failure_is_fail_closed_and_audited(
    client, db_session, make_account
) -> None:
    account = make_account("redis-failure@vena-ia.dev")
    original = client.app.state.auth_security_store
    client.app.state.auth_security_store = UnavailableSecurityStore()
    try:
        login = client.post(
            "/auth/login",
            json={"email": account.email, "password": "irrelevant"},
        )
        session = client.get("/auth/me", headers=account.headers)
        logout = client.post("/auth/logout", headers=account.headers)
    finally:
        client.app.state.auth_security_store = original

    assert login.status_code == 503
    assert session.status_code == 503
    assert logout.status_code == 503
    events = list(
        db_session.scalars(
            select(SecurityAuditEvent).where(
                SecurityAuditEvent.event_type == "SECURITY_STORE_UNAVAILABLE"
            )
        )
    )
    assert {event.reason for event in events} == {
        "LOGIN_RATE_LIMIT",
        "TOKEN_REVOCATION_LOOKUP",
        "TOKEN_REVOCATION_WRITE",
    }
    assert all(event.outcome == "ERROR" for event in events)
    assert "Bearer " not in str([(event.reason, event.origin) for event in events])
