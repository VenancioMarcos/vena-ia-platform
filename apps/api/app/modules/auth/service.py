from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.schemas import UserRegister


class DuplicateIdentityError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class LegacyCredentialNotEligibleError(Exception):
    pass


class IdentityNotFoundError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def register(self, payload: UserRegister) -> User:
        existing = self._db.scalar(select(User).where(User.email == payload.email))
        if existing is not None:
            raise DuplicateIdentityError("Email already registered")

        user = User(
            name=payload.name,
            email=payload.email,
            role="member",
            password_hash=hash_password(
                payload.password,
                settings.password_hash_iterations,
            ),
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self._db.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        return user

    def set_legacy_credential(self, user_id: str, password: str) -> User:
        user = self._db.get(User, user_id)
        if user is None:
            raise IdentityNotFoundError("User not found")
        if user.password_hash is not None:
            raise LegacyCredentialNotEligibleError("Credential is already defined")
        user.password_hash = hash_password(password, settings.password_hash_iterations)
        user.auth_version += 1
        self._db.commit()
        self._db.refresh(user)
        return user
