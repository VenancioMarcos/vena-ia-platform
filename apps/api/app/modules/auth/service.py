from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.organizations.models import Membership, Organization
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
        self._db.flush()
        organization = Organization(name=f"{payload.name.strip()[:200]} — Beta Workspace")
        self._db.add(organization)
        self._db.flush()
        self._db.add(
            Membership(
                organization_id=organization.id,
                user_id=user.id,
                team_id=None,
                role="OWNER",
                created_by=user.id,
            )
        )
        defaults = (
            (
                "MATERIAL",
                "BETA1-STEEL",
                "Beta 1 review material",
                {"cutting_speed_m_min": 120, "feed_per_tooth_mm": 0.04},
            ),
            (
                "MACHINE",
                "BETA1-3AXIS-MILL",
                "Beta 1 controlled machine envelope",
                {"operations": ["milling"], "max_rpm": 8_000, "max_feed_mm_min": 3_000},
            ),
            (
                "TOOL",
                "BETA1-END-MILL",
                "Beta 1 controlled end mill",
                {"operations": ["milling"], "diameter_mm": 0.5, "teeth": 2},
            ),
        )
        for kind, code, name, properties in defaults:
            self._db.add(
                EngineeringCatalogItem(
                    kind=kind,
                    code=code,
                    name=name,
                    data_version="beta1-default-v1",
                    source="Vena_IA Beta 1 onboarding default; requires human review",
                    properties=properties,
                    scope_type="ORGANIZATION_OWNED",
                    organization_id=organization.id,
                    created_by=user.id,
                )
            )
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
