"""Shared pytest fixtures.

Tests use an in-memory SQLite database instead of PostgreSQL. This is a
deliberate, test-only substitution (see docs/DECISIONS.md, DEC-011): it keeps
the test suite fast and dependency-free, while PostgreSQL remains the only
officially adopted database for development and production (DEC-005).
"""

from collections.abc import Generator
from dataclasses import dataclass

import pytest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import models_registry  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.modules.users.models import User

TEST_PASSWORD = "correct-horse-battery-staple"


@dataclass(frozen=True)
class TestAccount:
    id: str
    email: str
    role: str
    headers: dict[str, str]

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_database(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setattr(
        settings,
        "auth_secret_key",
        "test-only-auth-secret-key-with-at-least-32-bytes",
    )
    monkeypatch.setattr(settings, "auth_cookie_secure", False)
    app.state.auth_rate_limiter.clear()
    app.state.revoked_auth_tokens.clear()
    Base.metadata.create_all(bind=engine)
    yield
    app.state.auth_rate_limiter.clear()
    app.state.revoked_auth_tokens.clear()
    Base.metadata.drop_all(bind=engine)


def _override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def make_account(client: TestClient):
    def factory(
        email: str = "member@vena-ia.dev",
        *,
        name: str = "Test User",
        role: str = "member",
    ) -> TestAccount:
        registered = client.post(
            "/auth/register",
            json={"name": name, "email": email, "password": TEST_PASSWORD},
        )
        assert registered.status_code == 201, registered.text
        user = registered.json()

        if role == "admin":
            db = TestingSessionLocal()
            try:
                stored = db.get(User, user["id"])
                assert stored is not None
                stored.role = "admin"
                db.commit()
            finally:
                db.close()

        logged_in = client.post(
            "/auth/login",
            json={"email": email, "password": TEST_PASSWORD},
        )
        assert logged_in.status_code == 200, logged_in.text
        token = logged_in.json()["access_token"]
        client.cookies.clear()
        return TestAccount(
            id=user["id"],
            email=email,
            role=role,
            headers={"Authorization": f"Bearer {token}"},
        )

    return factory


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
