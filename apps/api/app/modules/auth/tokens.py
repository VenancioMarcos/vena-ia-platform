"""Minimal HS256 JWT implementation with strict claim validation."""

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

_ALGORITHM = "HS256"
_ISSUER = "vena-ia-api"
_MIN_SECRET_BYTES = 32


class TokenConfigurationError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


@dataclass(frozen=True)
class TokenIdentity:
    user_id: str
    expires_at: datetime


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
    except (binascii.Error, ValueError, TypeError) as exc:
        raise InvalidTokenError("Invalid authentication token") from exc


def _secret(secret: str) -> bytes:
    encoded = secret.encode("utf-8")
    if len(encoded) < _MIN_SECRET_BYTES:
        raise TokenConfigurationError(
            "AUTH_SECRET_KEY must contain at least 32 bytes"
        )
    return encoded


def create_access_token(
    user_id: str,
    secret: str,
    expiration_minutes: int,
    *,
    now: datetime | None = None,
) -> tuple[str, datetime]:
    if not 1 <= expiration_minutes <= 1_440:
        raise TokenConfigurationError(
            "AUTH_TOKEN_EXPIRATION_MINUTES must be between 1 and 1440"
        )
    issued_at = now or datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=expiration_minutes)
    header = {"alg": _ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "iss": _ISSUER,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    header_segment = _encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_segment = _encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(_secret(secret), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_encode(signature)}", expires_at


def decode_access_token(
    token: str,
    secret: str,
    *,
    now: datetime | None = None,
) -> TokenIdentity:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise InvalidTokenError("Invalid authentication token") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected = hmac.new(_secret(secret), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _decode(signature_segment)):
        raise InvalidTokenError("Invalid authentication token")

    try:
        header = json.loads(_decode(header_segment))
        payload: dict[str, Any] = json.loads(_decode(payload_segment))
        user_id = payload["sub"]
        issuer = payload["iss"]
        expires = payload["exp"]
    except (json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError) as exc:
        raise InvalidTokenError("Invalid authentication token") from exc

    if header != {"alg": _ALGORITHM, "typ": "JWT"}:
        raise InvalidTokenError("Invalid authentication token")
    if issuer != _ISSUER or not isinstance(user_id, str) or not user_id:
        raise InvalidTokenError("Invalid authentication token")
    if not isinstance(expires, int):
        raise InvalidTokenError("Invalid authentication token")

    expires_at = datetime.fromtimestamp(expires, timezone.utc)
    current = now or datetime.now(timezone.utc)
    if expires_at <= current:
        raise InvalidTokenError("Authentication token has expired")
    return TokenIdentity(user_id=user_id, expires_at=expires_at)
