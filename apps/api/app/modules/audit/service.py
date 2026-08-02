from datetime import datetime

from fastapi import Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.audit.models import SecurityAuditEvent


def record_security_event(
    db: Session,
    request: Request,
    event_type: str,
    *,
    outcome: str,
    reason: str | None = None,
    actor_user_id: str | None = None,
    target_user_id: str | None = None,
) -> SecurityAuditEvent:
    origin = request.client.host if request.client is not None else "unknown-client"
    event = SecurityAuditEvent(
        event_type=event_type,
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        outcome=outcome,
        reason=reason,
        origin=origin,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_security_events(
    db: Session,
    *,
    event_type: str | None,
    user_id: str | None,
    since: datetime | None,
    until: datetime | None,
    offset: int,
    limit: int,
) -> list[SecurityAuditEvent]:
    statement = select(SecurityAuditEvent)
    if event_type is not None:
        statement = statement.where(SecurityAuditEvent.event_type == event_type)
    if user_id is not None:
        statement = statement.where(
            or_(
                SecurityAuditEvent.actor_user_id == user_id,
                SecurityAuditEvent.target_user_id == user_id,
            )
        )
    if since is not None:
        statement = statement.where(SecurityAuditEvent.occurred_at >= since)
    if until is not None:
        statement = statement.where(SecurityAuditEvent.occurred_at <= until)
    statement = statement.order_by(
        SecurityAuditEvent.occurred_at.desc(), SecurityAuditEvent.id.desc()
    )
    return list(db.scalars(statement.offset(offset).limit(limit)))
