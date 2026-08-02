from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import (
    AdminUserDependency,
    AuthServiceDependency,
    AuthorizationDependency,
)
from app.modules.auth.service import DuplicateIdentityError
from app.modules.auth.rate_limit import RegistrationRateLimitDependency
from app.modules.users.models import User
from app.modules.users.schemas import UserRead, UserRegister

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
