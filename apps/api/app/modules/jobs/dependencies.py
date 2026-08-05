from typing import Annotated

from fastapi import Depends, Request
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.documents.dependencies import DocumentServiceDependency
from app.modules.jobs.queue import JobQueue, MemoryJobQueue, RedisJobQueue
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.service import JobService

DatabaseDependency = Annotated[Session, Depends(get_db)]


def build_job_queue() -> JobQueue:
    if settings.jobs_queue_provider == "memory":
        return MemoryJobQueue()
    client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=settings.jobs_redis_timeout_seconds,
        socket_timeout=settings.jobs_redis_timeout_seconds,
        decode_responses=True,
    )
    return RedisJobQueue(client, settings.jobs_redis_prefix)


def get_job_queue(request: Request) -> JobQueue:
    return request.app.state.job_queue


JobQueueDependency = Annotated[JobQueue, Depends(get_job_queue)]


def get_job_service(
    db: DatabaseDependency,
    queue: JobQueueDependency,
    current_user: CurrentUserDependency,
    documents: DocumentServiceDependency,
) -> JobService:
    return JobService(
        JobRepository(db),
        queue,
        current_user,
        documents,
        max_attempts=settings.jobs_max_attempts,
        timeout_seconds=settings.jobs_timeout_seconds,
    )


JobServiceDependency = Annotated[JobService, Depends(get_job_service)]
