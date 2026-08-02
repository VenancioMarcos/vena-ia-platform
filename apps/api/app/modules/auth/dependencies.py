from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.audit.service import record_security_event
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.service import AuthService
from app.modules.auth.tokens import (
    InvalidTokenError,
    TokenConfigurationError,
    decode_access_token,
)
from app.modules.users.models import User


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def _authentication_error(detail: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
    session_cookie: Annotated[
        str | None,
        Cookie(alias=settings.auth_cookie_name),
    ] = None,
) -> User:
    token = session_cookie
    if authorization is not None:
        scheme, separator, credentials = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not credentials.strip():
            raise _authentication_error("Invalid authentication token")
        token = credentials.strip()
    if not token:
        raise _authentication_error()

    try:
        identity = decode_access_token(token, settings.auth_secret_key)
    except (InvalidTokenError, TokenConfigurationError):
        record_security_event(
            db,
            request,
            "TOKEN_REJECTED",
            outcome="DENIED",
            reason="INVALID_TOKEN",
        )
        raise _authentication_error("Invalid authentication token") from None

    if request.app.state.revoked_auth_tokens.contains(identity):
        record_security_event(
            db,
            request,
            "TOKEN_REJECTED",
            outcome="DENIED",
            reason="REVOKED_TOKEN",
            actor_user_id=identity.user_id,
        )
        raise _authentication_error("Invalid authentication token")

    user = db.get(User, identity.user_id)
    if user is None or user.auth_version != identity.auth_version:
        record_security_event(
            db,
            request,
            "TOKEN_REJECTED",
            outcome="DENIED",
            reason="UNKNOWN_OR_INVALIDATED_SESSION",
            actor_user_id=identity.user_id if user is not None else None,
        )
        raise _authentication_error("Invalid authentication token")
    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]


def require_admin(
    request: Request,
    current_user: CurrentUserDependency,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if current_user.role != "admin":
        record_security_event(
            db,
            request,
            "ADMIN_OPERATION_DENIED",
            outcome="DENIED",
            reason="ADMIN_REQUIRED",
            actor_user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative access required",
        )
    return current_user


AdminUserDependency = Annotated[User, Depends(require_admin)]


def get_authorization_service(
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUserDependency,
) -> AuthorizationService:
    return AuthorizationService(db, current_user)


AuthorizationDependency = Annotated[
    AuthorizationService,
    Depends(get_authorization_service),
]
