from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.metrics import safe_metric_call
from app.modules.audit.service import record_security_event
from app.modules.documents.service import DocumentAccessDeniedError, DocumentNotFoundError
from app.modules.jobs.dependencies import DatabaseDependency, JobServiceDependency
from app.modules.jobs.queue import JobQueueUnavailable
from app.modules.jobs.repository import InvalidJobTransitionError
from app.modules.jobs.schemas import JobCreateRequest, JobResponse
from app.modules.jobs.service import JobIdempotencyConflictError, JobNotFoundError

router = APIRouter(tags=["jobs"])


@router.post(
    "/documents/{document_id}/jobs/processing",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_document_processing_job(
    document_id: str,
    payload: JobCreateRequest,
    request: Request,
    response: Response,
    service: JobServiceDependency,
    db: DatabaseDependency,
) -> JobResponse:
    try:
        job, created = service.create_document_processing(
            document_id,
            payload.idempotency_key,
            getattr(request.state, "request_id", None),
            getattr(request.state, "correlation_id", None),
        )
        if not created:
            response.status_code = status.HTTP_200_OK
        if created:
            record_security_event(
                db,
                request,
                "job.created",
                outcome="success",
                reason=job.job_type,
                actor_user_id=job.owner_id,
            )
            safe_metric_call(
                request.app.state.metric_collector.increment,
                "async_jobs_total",
                {"job_type": job.job_type, "job_status": "queued"},
            )
        return JobResponse.model_validate(job)
    except (DocumentNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except JobIdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except JobQueueUnavailable as exc:
        safe_metric_call(
            request.app.state.alert_manager.emit,
            "job_queue_unavailable",
            "critical",
            context={"job_type": "document.processing"},
            correlation_id=getattr(request.state, "correlation_id", None),
        )
        raise HTTPException(
            status_code=503,
            detail=str(exc),
            headers={"X-Vena-Error-Code": "QUEUE_UNAVAILABLE"},
        ) from exc


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, service: JobServiceDependency) -> JobResponse:
    try:
        return JobResponse.model_validate(service.get(job_id))
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: str,
    request: Request,
    service: JobServiceDependency,
    db: DatabaseDependency,
) -> JobResponse:
    try:
        job = service.cancel(job_id)
        record_security_event(
            db,
            request,
            "job.cancel_requested",
            outcome="success",
            reason=job.status,
            actor_user_id=job.owner_id,
        )
        return JobResponse.model_validate(job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidJobTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
def retry_job(
    job_id: str,
    request: Request,
    service: JobServiceDependency,
    db: DatabaseDependency,
) -> JobResponse:
    try:
        job = service.retry(job_id)
        record_security_event(
            db,
            request,
            "job.retry_requested",
            outcome="success",
            reason=job.job_type,
            actor_user_id=job.owner_id,
        )
        return JobResponse.model_validate(job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidJobTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except JobQueueUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
            headers={"X-Vena-Error-Code": "QUEUE_UNAVAILABLE"},
        ) from exc
