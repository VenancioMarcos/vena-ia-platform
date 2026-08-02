from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.modules.auth.tokens import InvalidTokenError, create_access_token, decode_access_token
from app.modules.users.models import User

PASSWORD = "correct-horse-battery-staple"


def _register(client, email: str = "secure@vena-ia.dev"):
    return client.post(
        "/auth/register",
        json={"name": "Secure User", "email": email, "password": PASSWORD},
    )


def _login(client, email: str = "secure@vena-ia.dev", password: str = PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register_hashes_password_and_forces_member_role(client, db_session) -> None:
    response = _register(client)

    assert response.status_code == 201
    assert response.json()["role"] == "member"
    assert "password" not in response.json()

    user = db_session.scalar(select(User).where(User.email == "secure@vena-ia.dev"))
    assert user is not None
    assert user.password_hash is not None
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("pbkdf2_sha256$")


def test_registration_rejects_client_selected_admin_role(client) -> None:
    response = client.post(
        "/auth/register",
        json={
            "name": "Attacker",
            "email": "attacker@vena-ia.dev",
            "password": PASSWORD,
            "role": "admin",
        },
    )

    assert response.status_code == 422


def test_valid_login_returns_signed_token_and_cookie(client) -> None:
    _register(client)

    response = _login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"].count(".") == 2
    assert settings.auth_cookie_name in response.cookies

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "secure@vena-ia.dev"


def test_invalid_login_is_rejected(client) -> None:
    _register(client)

    response = _login(client, password="definitely-wrong")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_missing_token_is_rejected(client) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_invalid_token_is_rejected(client) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_expired_token_is_rejected(client) -> None:
    registered = _register(client).json()
    token, _ = create_access_token(
        registered["id"],
        settings.auth_secret_key,
        expiration_minutes=1,
        now=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_issued_in_the_future_is_rejected() -> None:
    now = datetime.now(timezone.utc)
    token, _ = create_access_token(
        "future-user",
        settings.auth_secret_key,
        expiration_minutes=5,
        now=now + timedelta(minutes=1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token, settings.auth_secret_key, now=now)


def test_x_user_id_does_not_authenticate(client) -> None:
    registered = _register(client).json()

    response = client.get("/auth/me", headers={"X-User-ID": registered["id"]})

    assert response.status_code == 401


def test_logout_clears_session(client) -> None:
    _register(client)
    _login(client)

    logged_out = client.post("/auth/logout")
    me = client.get("/auth/me")

    assert logged_out.status_code == 204
    assert me.status_code == 401


def test_logout_revokes_cookie_token_against_reuse(client) -> None:
    _register(client)
    _login(client)
    token = client.cookies.get(settings.auth_cookie_name)
    assert token is not None

    assert client.post("/auth/logout").status_code == 204
    reused = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert reused.status_code == 401


def test_logout_revokes_bearer_without_affecting_another_session(client) -> None:
    first = _register(client, "first-session@vena-ia.dev").json()
    first_login = _login(client, first["email"]).json()
    client.cookies.clear()
    second = _register(client, "second-session@vena-ia.dev").json()
    second_login = _login(client, second["email"]).json()
    client.cookies.clear()

    logged_out = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {first_login['access_token']}"},
    )
    first_reused = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {first_login['access_token']}"},
    )
    second_active = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {second_login['access_token']}"},
    )

    assert logged_out.status_code == 204
    assert first_reused.status_code == 401
    assert second_active.status_code == 200


def test_logout_revokes_both_cookie_and_bearer_tokens(client) -> None:
    cookie_user = _register(client, "cookie-session@vena-ia.dev").json()
    _login(client, cookie_user["email"])
    cookie_token = client.cookies.get(settings.auth_cookie_name)
    assert cookie_token is not None

    bearer_user = _register(client, "bearer-session@vena-ia.dev").json()
    bearer_token = _login(client, bearer_user["email"]).json()["access_token"]
    client.cookies.set(settings.auth_cookie_name, cookie_token)

    logged_out = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )

    assert logged_out.status_code == 204
    for token in (cookie_token, bearer_token):
        reused = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert reused.status_code == 401


def test_logout_is_idempotent_for_invalid_token(client) -> None:
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 204
    set_cookie = response.headers["set-cookie"]
    assert set_cookie.startswith(f"{settings.auth_cookie_name}=")
    assert "Max-Age=0" in set_cookie
