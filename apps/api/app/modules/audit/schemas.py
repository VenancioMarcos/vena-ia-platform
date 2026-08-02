from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityAuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    occurred_at: datetime
    actor_user_id: str | None
    target_user_id: str | None
    outcome: str
    reason: str | None
    origin: str
