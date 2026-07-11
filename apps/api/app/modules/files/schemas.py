from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileCreate(BaseModel):
    project_id: str
    filename: str
    type: str
    storage_key: str | None = None


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    filename: str
    type: str
    storage_key: str | None
    created_at: datetime
