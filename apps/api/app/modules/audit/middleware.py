"""Persist bounded domain audit events after mutating HTTP requests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.modules.audit.service import record_security_event

_AUDITED_MUTATIONS = {
    ("POST", "/projects"): "PROJECT_CREATED",
    ("POST", "/projects/{project_id}/documents"): "DOCUMENT_UPLOADED",
    ("DELETE", "/documents/{document_id}"): "DOCUMENT_DELETED",
    ("DELETE", "/projects/{project_id}/documents/{document_id}"): "DOCUMENT_DELETED",
    ("POST", "/documents/{document_id}/process"): "DOCUMENT_PROCESSING_REQUESTED",
    ("POST", "/documents/{document_id}/processing"): "DOCUMENT_PROCESSING_EXECUTED",
    ("POST", "/documents/{document_id}/embeddings"): "DOCUMENT_INDEXING_EXECUTED",
    ("POST", "/projects/{project_id}/knowledge/ask"): "KNOWLEDGE_QUERY_EXECUTED",
    ("POST", "/chat/{project_id}/messages"): "CHAT_MESSAGE_CREATED",
    ("POST", "/chat/{project_id}/ask"): "CHAT_RESPONSE_GENERATED",
    ("POST", "/research/reports"): "REPORT_CREATED",
}


class AuditCorrelationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, *, session_factory: Callable[[], Session]) -> None:
        super().__init__(app)
        self._session_factory = session_factory

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        event_type = _AUDITED_MUTATIONS.get((request.method, route_path))
        if event_type is None:
            return response
        db = self._session_factory()
        try:
            record_security_event(
                db,
                request,
                event_type,
                outcome="ALLOWED" if response.status_code < 400 else "DENIED",
                reason=f"HTTP_{response.status_code}",
                actor_user_id=getattr(request.state, "authenticated_user_id", None),
            )
        except Exception:
            db.rollback()
            try:
                request.app.state.metric_collector.increment(
                    "dependency_failures_total", {"dependency": "postgresql"}
                )
                request.app.state.alert_manager.emit(
                    "dependency_unavailable",
                    "critical",
                    context={"dependency": "postgresql"},
                )
            except Exception:
                pass
        finally:
            db.close()
        return response
