"""Preliminary dependency readiness checks with no sensitive diagnostics."""

from __future__ import annotations

from typing import Protocol

from minio import Minio
from redis import Redis
from sqlalchemy import text
from urllib3 import PoolManager, Timeout

from app.core.config import Settings
from app.core.database import engine
from app.modules.jobs.queue import RedisJobQueue


class ReadinessChecker(Protocol):
    def check(self) -> dict[str, str]: ...


class DefaultReadinessChecker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def check(self) -> dict[str, str]:
        statuses: dict[str, str] = {}
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            statuses["postgresql"] = "ready"
        except Exception:
            statuses["postgresql"] = "unavailable"
        try:
            redis = Redis.from_url(
                self.settings.redis_url,
                socket_connect_timeout=self.settings.auth_redis_timeout_seconds,
                socket_timeout=self.settings.auth_redis_timeout_seconds,
            )
            statuses["redis"] = "ready" if redis.ping() else "unavailable"
            job_queue = RedisJobQueue(redis, self.settings.jobs_redis_prefix)
            statuses["worker"] = (
                "ready" if job_queue.worker_available() else "unavailable"
            )
        except Exception:
            statuses["redis"] = "unavailable"
            statuses["worker"] = "unavailable"
        try:
            minio = Minio(
                self.settings.minio_endpoint,
                access_key=self.settings.minio_access_key,
                secret_key=self.settings.minio_secret_key,
                secure=self.settings.minio_secure,
                http_client=PoolManager(
                    timeout=Timeout(
                        connect=self.settings.minio_connect_timeout_seconds,
                        read=self.settings.minio_read_timeout_seconds,
                    ),
                    retries=False,
                ),
            )
            statuses["minio"] = (
                "ready" if minio.bucket_exists(self.settings.minio_bucket) else "unavailable"
            )
        except Exception:
            statuses["minio"] = "unavailable"
        return statuses
