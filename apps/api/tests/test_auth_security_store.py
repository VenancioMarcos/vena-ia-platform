from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import os
from threading import Lock
from typing import Any, cast
from uuid import uuid4

import pytest
from pydantic import ValidationError
from redis import Redis
from redis.exceptions import ConnectionError

from app.core.config import Settings
from app.core.rate_limit import RateLimitExceeded
from app.modules.auth.security_store import (
    RedisAuthenticationSecurityStore,
    SecurityStoreUnavailable,
)
from app.modules.auth.tokens import TokenIdentity


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int | str] = {}
        self.ttls: dict[str, int] = {}
        self.fail = False
        self.lock = Lock()

    def eval(self, _script: str, _keys: int, key: str, window: str) -> list[int]:
        if self.fail:
            raise ConnectionError("unavailable")
        with self.lock:
            value = int(self.values.get(key, 0)) + 1
            self.values[key] = value
            self.ttls.setdefault(key, int(window))
            return [value, self.ttls[key]]

    def set(self, key: str, value: str, *, ex: int, nx: bool) -> bool:
        if self.fail:
            raise ConnectionError("unavailable")
        if nx and key in self.values:
            return False
        self.values[key] = value
        self.ttls[key] = ex
        return True

    def exists(self, key: str) -> int:
        if self.fail:
            raise ConnectionError("unavailable")
        return int(key in self.values)


def _store(client: FakeRedis) -> RedisAuthenticationSecurityStore:
    return RedisAuthenticationSecurityStore(cast(Redis, cast(Any, client)), "vena:test")


def _identity(fingerprint: str = "token-fingerprint") -> TokenIdentity:
    return TokenIdentity(
        user_id="user-1",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
        fingerprint=fingerprint,
        auth_version=2,
    )


def test_rate_limit_is_shared_between_store_instances_and_hides_origin() -> None:
    client = FakeRedis()
    first = _store(client)
    second = _store(client)

    first.consume("auth:login:203.0.113.10", limit=1, window_seconds=30)
    with pytest.raises(RateLimitExceeded) as exceeded:
        second.consume("auth:login:203.0.113.10", limit=1, window_seconds=30)

    assert exceeded.value.retry_after_seconds == 30
    assert all("203.0.113.10" not in key for key in client.values)
    assert all(client.ttls[key] == 30 for key in client.values)


def test_rate_limit_atomicity_under_concurrency() -> None:
    client = FakeRedis()
    stores = [_store(client), _store(client)]

    def consume(index: int) -> bool:
        try:
            stores[index % 2].consume("auth:login:client", limit=5, window_seconds=30)
            return True
        except RateLimitExceeded:
            return False

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(consume, range(20)))

    assert results.count(True) == 5
    assert results.count(False) == 15


def test_distributed_revocation_uses_fingerprint_digest_and_token_ttl() -> None:
    client = FakeRedis()
    first = _store(client)
    second = _store(client)
    identity = _identity()

    first.revoke(identity)

    assert second.contains(identity)
    assert all(identity.fingerprint not in key for key in client.values)
    assert 1 <= next(iter(client.ttls.values())) <= 60


@pytest.mark.parametrize("operation", ["consume", "revoke", "contains"])
def test_redis_failures_are_fail_closed(operation: str) -> None:
    client = FakeRedis()
    client.fail = True
    store = _store(client)

    with pytest.raises(SecurityStoreUnavailable):
        if operation == "consume":
            store.consume("auth:login:test", limit=1, window_seconds=30)
        elif operation == "revoke":
            store.revoke(_identity())
        else:
            store.contains(_identity())


@pytest.mark.skipif(
    os.getenv("RUN_REDIS_INTEGRATION") != "1",
    reason="real Redis integration is explicitly enabled",
)
def test_real_redis_shares_limits_and_revocations() -> None:
    client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    prefix = f"vena:test:{uuid4().hex}"
    first = RedisAuthenticationSecurityStore(client, prefix)
    second = RedisAuthenticationSecurityStore(client, prefix)
    identity = _identity(uuid4().hex)
    try:
        first.consume("auth:login:integration", limit=1, window_seconds=30)
        with pytest.raises(RateLimitExceeded):
            second.consume("auth:login:integration", limit=1, window_seconds=30)
        first.revoke(identity)
        assert second.contains(identity)
        keys = list(client.scan_iter(f"{prefix}:*"))
        assert keys
        assert all(identity.fingerprint not in key for key in keys)
        assert all(client.ttl(key) > 0 for key in keys)
    finally:
        keys = list(client.scan_iter(f"{prefix}:*"))
        if keys:
            client.delete(*keys)


@pytest.mark.parametrize(
    "values",
    [
        {"auth_security_store": "invalid"},
        {"auth_redis_prefix": ":invalid"},
        {"auth_redis_timeout_seconds": 0},
        {"app_env": "production", "auth_security_store": "memory"},
    ],
)
def test_invalid_security_store_configuration_is_rejected(
    values: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)
