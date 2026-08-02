"""Rate-limit dependencies for unauthenticated authentication routes."""

from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import RateLimitExceeded
from app.modules.audit.service import record_security_event
from app.modules.auth.security_store import (
    AuthenticationSecurityStore,
    SecurityStoreUnavailable,
)

AuthRateLimitScope = Literal["login", "registration"]


def get_auth_security_store(request: Request) -> AuthenticationSecurityStore:
    return request.app.state.auth_security_store


AuthSecurityStoreDependency = Annotated[
    AuthenticationSecurityStore,
    Depends(get_auth_security_store),
]


def _client_key(request: Request) -> str:
    # Forwarded headers are intentionally ignored until a trusted proxy boundary
    # is configured. X-User-ID is never an identity or rate-limit key.
    return request.client.host if request.client is not None else "unknown-client"


def _enforce(
    scope: AuthRateLimitScope,
    request: Request,
    store: AuthSecurityStoreDependency,
    db: Session,
) -> None:
    if scope == "login":
        limit = settings.auth_login_rate_limit_requests
    else:
        limit = settings.auth_registration_rate_limit_requests

    try:
        store.consume(
            f"auth:{scope}:{_client_key(request)}",
            limit=limit,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )
    except SecurityStoreUnavailable as exc:
        record_security_event(
            db,
            request,
            "SECURITY_STORE_UNAVAILABLE",
            outcome="ERROR",
            reason=f"{scope.upper()}_RATE_LIMIT",
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication security control unavailable",
        ) from exc
    except RateLimitExceeded as exc:
        record_security_event(
            db,
            request,
            "RATE_LIMIT_EXCEEDED",
            outcome="DENIED",
            reason=scope.upper(),
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc


def enforce_login_rate_limit(
    request: Request,
    store: AuthSecurityStoreDependency,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    _enforce("login", request, store, db)


def enforce_registration_rate_limit(
    request: Request,
    store: AuthSecurityStoreDependency,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    _enforce("registration", request, store, db)


LoginRateLimitDependency = Annotated[None, Depends(enforce_login_rate_limit)]
RegistrationRateLimitDependency = Annotated[
    None,
    Depends(enforce_registration_rate_limit),
]
