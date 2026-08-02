import pytest

from app.core.rate_limit import FixedWindowRateLimiter, RateLimitExceeded


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_fixed_window_blocks_and_reports_retry_after() -> None:
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(clock)

    limiter.consume("auth:login:client", limit=2, window_seconds=10)
    limiter.consume("auth:login:client", limit=2, window_seconds=10)

    with pytest.raises(RateLimitExceeded) as raised:
        limiter.consume("auth:login:client", limit=2, window_seconds=10)

    assert raised.value.retry_after_seconds == 10


def test_fixed_window_resets_and_keeps_keys_isolated() -> None:
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(clock)

    limiter.consume("auth:login:client-a", limit=1, window_seconds=10)
    limiter.consume("auth:login:client-b", limit=1, window_seconds=10)
    clock.advance(10)
    limiter.consume("auth:login:client-a", limit=1, window_seconds=10)


@pytest.mark.parametrize(
    ("limit", "window_seconds"),
    [(0, 10), (1, 0)],
)
def test_fixed_window_rejects_invalid_configuration(
    limit: int,
    window_seconds: int,
) -> None:
    limiter = FixedWindowRateLimiter()

    with pytest.raises(ValueError):
        limiter.consume("key", limit=limit, window_seconds=window_seconds)


def test_login_rate_limit_returns_429_and_retry_after(client, monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.auth_login_rate_limit_requests", 2)
    registered = client.post(
        "/auth/register",
        json={
            "name": "Rate Limited",
            "email": "rate-login@vena-ia.dev",
            "password": "correct-horse-battery-staple",
        },
    )
    assert registered.status_code == 201

    for _ in range(2):
        rejected = client.post(
            "/auth/login",
            json={"email": "rate-login@vena-ia.dev", "password": "wrong-password"},
        )
        assert rejected.status_code == 401

    limited = client.post(
        "/auth/login",
        json={"email": "rate-login@vena-ia.dev", "password": "wrong-password"},
    )

    assert limited.status_code == 429
    assert limited.json() == {"detail": "Too many authentication attempts"}
    assert 1 <= int(limited.headers["Retry-After"]) <= 60


def test_forwarded_headers_do_not_bypass_login_limit(client, monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.auth_login_rate_limit_requests", 1)

    first = client.post(
        "/auth/login",
        headers={"X-Forwarded-For": "198.51.100.10", "X-User-ID": "attacker-a"},
        json={"email": "missing@vena-ia.dev", "password": "wrong-password"},
    )
    second = client.post(
        "/auth/login",
        headers={"X-Forwarded-For": "203.0.113.20", "X-User-ID": "attacker-b"},
        json={"email": "missing@vena-ia.dev", "password": "wrong-password"},
    )

    assert first.status_code == 401
    assert second.status_code == 429


def test_registration_endpoints_share_the_same_limit(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.config.settings.auth_registration_rate_limit_requests",
        2,
    )
    password = "correct-horse-battery-staple"

    first = client.post(
        "/auth/register",
        json={"name": "First", "email": "first-limit@vena-ia.dev", "password": password},
    )
    second = client.post(
        "/users",
        json={"name": "Second", "email": "second-limit@vena-ia.dev", "password": password},
    )
    limited = client.post(
        "/auth/register",
        json={"name": "Third", "email": "third-limit@vena-ia.dev", "password": password},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert limited.status_code == 429
