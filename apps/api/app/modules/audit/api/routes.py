from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.audit.models import SecurityAuditEvent
from app.modules.audit.schemas import SecurityAuditEventRead
from app.modules.audit.service import list_security_events
from app.modules.auth.dependencies import AdminUserDependency

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/security-events", response_model=list[SecurityAuditEventRead])
def security_events(
    _admin: AdminUserDependency,
    db: Annotated[Session, Depends(get_db)],
    event_type: str | None = Query(default=None, max_length=64),
    user_id: str | None = Query(default=None, max_length=36),
    request_id: str | None = Query(default=None, min_length=36, max_length=36),
    correlation_id: str | None = Query(default=None, min_length=36, max_length=36),
    since: datetime | None = None,
    until: datetime | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SecurityAuditEvent]:
    return list_security_events(
        db,
        event_type=event_type,
        user_id=user_id,
        request_id=request_id,
        correlation_id=correlation_id,
        since=since,
        until=until,
        offset=offset,
        limit=limit,
    )
