"""Database engine, session factory and declarative base for the Vena_IA API.

Models live inside each domain module (app/modules/<domain>/models.py) and
share this single `Base`, so that Alembic autogeneration can discover all
tables via `Base.metadata`.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_postgres_connect_args = (
    {"connect_timeout": settings.postgresql_connect_timeout_seconds}
    if settings.database_url.startswith("postgresql")
    else {}
)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_timeout=settings.postgresql_pool_timeout_seconds,
    connect_args=_postgres_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
