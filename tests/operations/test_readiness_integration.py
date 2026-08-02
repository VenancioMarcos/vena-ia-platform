import os

import pytest
from minio import Minio

from app.core.config import settings
from app.core.readiness import DefaultReadinessChecker

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_READINESS_INTEGRATION") != "1",
    reason="Readiness integration is explicitly enabled",
)


def test_postgresql_redis_and_minio_are_ready_together() -> None:
    minio = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    if not minio.bucket_exists(settings.minio_bucket):
        minio.make_bucket(settings.minio_bucket)
    assert DefaultReadinessChecker(settings).check() == {
        "postgresql": "ready",
        "redis": "ready",
        "minio": "ready",
    }
