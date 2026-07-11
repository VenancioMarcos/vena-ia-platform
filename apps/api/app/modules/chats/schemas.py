from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    project_id: str
    title: str = "Chat"


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    created_at: datetime


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    role: str
    content: str
    created_at: datetime
