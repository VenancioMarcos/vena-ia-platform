from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.audit.service import record_security_event
from app.modules.auth.dependencies import (
    AdminUserDependency,
    AuthServiceDependency,
    AuthorizationDependency,
)
from app.modules.auth.service import (
    DuplicateIdentityError,
    IdentityNotFoundError,
    LegacyCredentialNotEligibleError,
)
from app.modules.auth.rate_limit import RegistrationRateLimitDependency
from app.modules.users.models import User
from app.modules.users.schemas import AdminCredentialSet, UserRead, UserRegister

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    _admin: AdminUserDependency,
    db: Session = Depends(get_db),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at)))


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserRegister,
    service: AuthServiceDependency,
    _rate_limit: RegistrationRateLimitDependency,
) -> User:
    """Compatibility registration endpoint; role is always assigned by the server."""
    try:
        return service.register(payload)
    except DuplicateIdentityError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, authorization: AuthorizationDependency) -> User:
    return authorization.require_user_access(user_id)


@router.put("/{user_id}/credentials", response_model=UserRead)
def set_legacy_credential(
    user_id: str,
    payload: AdminCredentialSet,
    request: Request,
    admin: AdminUserDependency,
    service: AuthServiceDependency,
    db: Session = Depends(get_db),
) -> User:
    if user_id == admin.id:
        record_security_event(
            db,
            request,
            "LEGACY_CREDENTIAL_RESET_DENIED",
            outcome="DENIED",
            reason="SELF_TARGET",
            actor_user_id=admin.id,
            target_user_id=admin.id,
        )
        raise HTTPException(status_code=403, detail="Administrative self-reset is not allowed")
    try:
        user = service.set_legacy_credential(user_id, payload.password)
    except IdentityNotFoundError as exc:
        record_security_event(
            db,
            request,
            "LEGACY_CREDENTIAL_RESET_DENIED",
            outcome="DENIED",
            reason="USER_NOT_FOUND",
            actor_user_id=admin.id,
        )
        raise HTTPException(status_code=404, detail="User not found") from exc
    except LegacyCredentialNotEligibleError as exc:
        record_security_event(
            db,
            request,
            "LEGACY_CREDENTIAL_RESET_DENIED",
            outcome="DENIED",
            reason="CREDENTIAL_ALREADY_DEFINED",
            actor_user_id=admin.id,
            target_user_id=user_id,
        )
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    record_security_event(
        db,
        request,
        "LEGACY_CREDENTIAL_SET",
        outcome="ALLOWED",
        actor_user_id=admin.id,
        target_user_id=user.id,
    )
    return user
