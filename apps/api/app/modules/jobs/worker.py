from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.alerts import AlertManager, NoOpAlertProvider
from app.core.metrics import NoOpMetricCollector, safe_metric_call
from app.core.observability import emit_structured_event, observability_context
from app.core.tracing import NoOpTraceProvider, Tracer
from app.modules.audit.service import record_system_security_event
from app.modules.jobs.contracts import JobStatus
from app.modules.jobs.models import Job
from app.modules.jobs.queue import InvalidJobQueueMessage, JobQueue, JobQueueUnavailable
from app.modules.jobs.repository import InvalidJobTransitionError, JobRepository
from app.modules.jobs.service import JobNotFoundError, WorkerJobService

JobHandler = Callable[[Job, Callable[[int], None], Callable[[], bool]], None]
SessionFactory = Callable[[], Session]


@dataclass(frozen=True, slots=True)
class WorkerResult:
    job_id: str | None
    outcome: str


class JobWorker:
    """Single-claim worker runner. It never executes user-supplied code or payloads."""

    def __init__(
        self,
        session_factory: SessionFactory,
        queue: JobQueue,
        handlers: dict[str, JobHandler],
        *,
        worker_id: str,
        lease_seconds: int,
        retry_base_seconds: float,
        monotonic: Callable[[], float] = time.monotonic,
        logger: logging.Logger | None = None,
        metric_collector: object | None = None,
        alert_manager: object | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self._sessions = session_factory
        self._queue = queue
        self._handlers = handlers
        self._worker_id = worker_id
        self._lease_seconds = lease_seconds
        self._retry_base = retry_base_seconds
        self._monotonic = monotonic
        self._logger = logger or logging.getLogger("vena_ia.worker")
        self._metrics = metric_collector or NoOpMetricCollector()
        self._alerts = alert_manager or AlertManager(NoOpAlertProvider())
        self._tracer = tracer or Tracer(NoOpTraceProvider())

    def run_once(self) -> WorkerResult:
        try:
            self._queue.heartbeat(self._worker_id, max(self._lease_seconds * 2, 10))
            recovered = self._queue.recover_abandoned()
            claimed = self._queue.claim(self._worker_id, self._lease_seconds)
        except InvalidJobQueueMessage as exc:
            return self._reject_invalid_message(exc.job_id)
        except JobQueueUnavailable:
            safe_metric_call(
                getattr(self._alerts, "emit", None),
                "job_queue_unavailable",
                "critical",
                context={"job_type": "document.processing"},
            )
            return WorkerResult(None, "queue_unavailable")
        if recovered:
            safe_metric_call(
                getattr(self._metrics, "increment", None),
                "job_queue_recoveries_total",
                {},
                recovered,
            )
        if claimed is None:
            return WorkerResult(None, "idle")
        message = claimed.message
        started = self._monotonic()
        session = self._sessions()
        service = WorkerJobService(JobRepository(session))
        try:
            with observability_context(message.request_id, message.correlation_id):
                job = service.start(message.job_id)
                self._queue.extend_lease(
                    job.id,
                    self._worker_id,
                    max(self._lease_seconds, job.timeout_seconds + self._lease_seconds),
                )
                self._observe(job, "running", session, "job.started")
                handler = self._handlers.get(job.job_type)
                if handler is None:
                    service.fail_terminal(
                        job.id, "JOB_TYPE_NOT_ALLOWED", "Job type is not allowlisted"
                    )
                    self._observe(job, "failed", session, "job.failed")
                    self._queue.acknowledge(job.id, self._worker_id)
                    return WorkerResult(job.id, "failed")

                def report(progress: int) -> None:
                    service.progress(job.id, progress)
                    emit_structured_event(
                        "job.progress",
                        job_id=job.id,
                        job_type=job.job_type,
                        job_status="running",
                        progress=progress,
                    )

                def cancelled() -> bool:
                    session.expire_all()
                    current = JobRepository(session).get(job.id)
                    return bool(
                        current
                        and current.status == JobStatus.CANCELLATION_REQUESTED.value
                    )

                with self._tracer.start_span("job.execute") as span:
                    try:
                        handler(job, report, cancelled)
                    except Exception as exc:
                        span.set_error(type(exc).__name__)
                        raise
                elapsed = self._monotonic() - started
                if service.cancel_if_requested(job.id):
                    outcome = "cancelled"
                elif elapsed > job.timeout_seconds:
                    service.time_out(job.id)
                    safe_metric_call(
                        getattr(self._alerts, "emit", None),
                        "job_timed_out",
                        "warning",
                        context={"job_type": job.job_type},
                        correlation_id=message.correlation_id,
                    )
                    outcome = "timed_out"
                else:
                    service.succeed(job.id)
                    outcome = "succeeded"
                self._observe(job, outcome, session, f"job.{outcome}", elapsed)
                self._queue.acknowledge(job.id, self._worker_id)
                return WorkerResult(job.id, outcome)
        except (JobNotFoundError, InvalidJobTransitionError):
            self._queue.acknowledge(message.job_id, self._worker_id)
            return WorkerResult(message.job_id, "discarded")
        except Exception as exc:
            session.rollback()
            failed_job = JobRepository(session).get(message.job_id)
            if failed_job is None:
                self._queue.acknowledge(message.job_id, self._worker_id)
                return WorkerResult(message.job_id, "discarded")
            if failed_job.status in {
                JobStatus.SUCCEEDED.value,
                JobStatus.FAILED.value,
                JobStatus.CANCELLED.value,
                JobStatus.TIMED_OUT.value,
            }:
                safe_metric_call(
                    getattr(self._alerts, "emit", None),
                    "job_queue_unavailable",
                    "critical",
                    context={"job_type": failed_job.job_type},
                    correlation_id=message.correlation_id,
                )
                return WorkerResult(failed_job.id, failed_job.status.lower())
            if failed_job.status == JobStatus.CANCELLATION_REQUESTED.value:
                WorkerJobService(JobRepository(session)).cancel_if_requested(failed_job.id)
                try:
                    self._queue.acknowledge(failed_job.id, self._worker_id)
                except JobQueueUnavailable:
                    pass
                with observability_context(message.request_id, message.correlation_id):
                    self._observe(failed_job, "cancelled", session, "job.cancelled")
                return WorkerResult(failed_job.id, "cancelled")
            delay = self._retry_base * (2 ** max(failed_job.attempt - 1, 0))
            failed = WorkerJobService(JobRepository(session)).fail(
                failed_job.id,
                "JOB_EXECUTION_FAILED",
                "Job execution failed; inspect correlated operator logs",
                delay,
            )
            if failed.status == JobStatus.RETRY_SCHEDULED.value:
                outcome = "retry_scheduled"
                try:
                    self._queue.retry(message, self._worker_id, delay)
                except JobQueueUnavailable:
                    safe_metric_call(
                        getattr(self._alerts, "emit", None),
                        "job_queue_unavailable",
                        "critical",
                        context={"job_type": failed_job.job_type},
                        correlation_id=message.correlation_id,
                    )
            else:
                try:
                    self._queue.acknowledge(failed_job.id, self._worker_id)
                except JobQueueUnavailable:
                    pass
                safe_metric_call(
                    getattr(self._alerts, "emit", None),
                    "job_retry_exhausted",
                    "critical",
                    context={"job_type": failed_job.job_type},
                    correlation_id=message.correlation_id,
                )
                outcome = "failed"
            with observability_context(message.request_id, message.correlation_id):
                self._observe(failed_job, outcome, session, f"job.{outcome}")
            self._logger.warning(
                "job execution failed",
                extra={
                    "job_id": failed_job.id,
                    "job_type": failed_job.job_type,
                    "error_type": type(exc).__name__,
                },
            )
            return WorkerResult(failed_job.id, outcome)
        finally:
            session.close()

    def _reject_invalid_message(self, job_id: str) -> WorkerResult:
        session = self._sessions()
        try:
            service = WorkerJobService(JobRepository(session))
            job = service.start(job_id)
            service.fail_terminal(
                job.id,
                "JOB_PAYLOAD_INVALID",
                "Queue message failed contract validation",
            )
            self._observe(job, "failed", session, "job.failed")
            return WorkerResult(job.id, "failed")
        except (JobNotFoundError, InvalidJobTransitionError):
            return WorkerResult(job_id, "discarded")
        finally:
            session.close()

    def _observe(
        self,
        job: Job,
        status: str,
        session: Session,
        event: str,
        duration_seconds: float | None = None,
    ) -> None:
        emit_structured_event(
            event,
            "ERROR" if status in {"failed", "timed_out"} else "INFO",
            job_id=job.id,
            job_type=job.job_type,
            job_status=status,
        )
        safe_metric_call(
            getattr(self._metrics, "increment", None),
            "async_jobs_total",
            {"job_type": job.job_type, "job_status": status},
        )
        if duration_seconds is not None:
            safe_metric_call(
                getattr(self._metrics, "observe", None),
                "async_job_duration_ms",
                {"job_type": job.job_type, "job_status": status},
                duration_seconds * 1_000,
            )
        try:
            record_system_security_event(
                session,
                event,
                outcome=status,
                reason=job.job_type,
                actor_user_id=job.owner_id,
            )
        except Exception:
            session.rollback()
