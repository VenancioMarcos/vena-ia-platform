import os

import pytest

from app.core.config import settings
from app.core.readiness import DefaultReadinessChecker

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_READINESS_INTEGRATION") != "1",
    reason="Readiness integration is explicitly enabled",
)


def test_postgresql_redis_and_minio_are_ready_together() -> None:
    assert DefaultReadinessChecker(settings).check() == {
        "postgresql": "ready",
        "redis": "ready",
        "minio": "ready",
    }
