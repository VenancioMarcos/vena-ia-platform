"""Shared authentication security controls backed by Redis in production."""

import hashlib
from datetime import datetime, timezone
from math import ceil
from typing import Protocol, cast

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import Settings
from app.core.rate_limit import FixedWindowRateLimiter, RateLimitExceeded
from app.modules.auth.tokens import RevokedTokenStore, TokenIdentity


class SecurityStoreUnavailable(Exception):
    """The mandatory distributed authentication control is unavailable."""


class AuthenticationSecurityStore(Protocol):
    def consume(self, key: str, *, limit: int, window_seconds: int) -> None: ...

    def revoke(self, identity: TokenIdentity) -> None: ...

    def contains(self, identity: TokenIdentity) -> bool: ...

    def clear(self) -> None: ...


class MemoryAuthenticationSecurityStore:
    """Explicit development/test-only security store."""

    def __init__(self) -> None:
        self._limiter = FixedWindowRateLimiter()
        self._revocations = RevokedTokenStore()

    def consume(self, key: str, *, limit: int, window_seconds: int) -> None:
        self._limiter.consume(key, limit=limit, window_seconds=window_seconds)

    def revoke(self, identity: TokenIdentity) -> None:
        self._revocations.revoke(identity)

    def contains(self, identity: TokenIdentity) -> bool:
        return self._revocations.contains(identity)

    def clear(self) -> None:
        self._limiter.clear()
        self._revocations.clear()


_CONSUME_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


class RedisAuthenticationSecurityStore:
    """Redis-backed rate limits and token revocations shared by all replicas."""

    def __init__(self, client: Redis, prefix: str) -> None:
        self._client = client
        self._prefix = prefix.rstrip(":")

    def _key(self, category: str, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"{self._prefix}:{category}:{digest}"

    def consume(self, key: str, *, limit: int, window_seconds: int) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("Rate limit and window must be positive")
        try:
            result = cast(
                list[int],
                self._client.eval(
                    _CONSUME_SCRIPT,
                    1,
                    self._key("rate", key),
                    str(window_seconds),
                ),
            )
            count, ttl = result[0], result[1]
        except (RedisError, TypeError, ValueError, IndexError) as exc:
            raise SecurityStoreUnavailable from exc
        if count > limit:
            raise RateLimitExceeded(max(1, ttl))

    def revoke(self, identity: TokenIdentity) -> None:
        ttl = ceil((identity.expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl <= 0:
            return
        try:
            self._client.set(
                self._key("revoked", identity.fingerprint),
                "1",
                ex=ttl,
                nx=True,
            )
        except RedisError as exc:
            raise SecurityStoreUnavailable from exc

    def contains(self, identity: TokenIdentity) -> bool:
        try:
            return bool(
                self._client.exists(self._key("revoked", identity.fingerprint))
            )
        except RedisError as exc:
            raise SecurityStoreUnavailable from exc

    def clear(self) -> None:
        """Not supported for the shared production store."""
        raise RuntimeError("Redis security store cannot be cleared globally")


def build_authentication_security_store(
    settings: Settings,
) -> AuthenticationSecurityStore:
    if settings.auth_security_store == "memory":
        return MemoryAuthenticationSecurityStore()
    client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=settings.auth_redis_timeout_seconds,
        socket_timeout=settings.auth_redis_timeout_seconds,
        decode_responses=True,
    )
    return RedisAuthenticationSecurityStore(client, settings.auth_redis_prefix)
