"""Password hashing based on PBKDF2-HMAC-SHA256 from the Python standard library."""

import base64
import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
_SALT_BYTES = 16
_HASH_BYTES = 32
_MIN_ITERATIONS = 100_000
_MAX_ITERATIONS = 2_000_000


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str, iterations: int) -> str:
    if not _MIN_ITERATIONS <= iterations <= _MAX_ITERATIONS:
        raise ValueError("Password hash iteration count is outside the safe range")
    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=_HASH_BYTES,
    )
    return f"{_ALGORITHM}${iterations}${_encode(salt)}${_encode(derived)}"


def verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        algorithm, raw_iterations, raw_salt, raw_expected = encoded.split("$", 3)
        iterations = int(raw_iterations)
        if algorithm != _ALGORITHM or not _MIN_ITERATIONS <= iterations <= _MAX_ITERATIONS:
            return False
        salt = _decode(raw_salt)
        expected = _decode(raw_expected)
        if len(salt) != _SALT_BYTES or len(expected) != _HASH_BYTES:
            return False
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=len(expected),
    )
    return hmac.compare_digest(actual, expected)
