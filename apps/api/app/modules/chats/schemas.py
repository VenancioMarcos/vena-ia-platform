from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: str
    title: str = Field(default="Chat", min_length=1, max_length=255)


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    created_at: datetime


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str = "user"
    content: str = Field(min_length=1, max_length=20_000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    user_id: str | None
    role: str
    content: str
    status: str
    evidence: list[dict[str, object]]
    error: str | None
    created_at: datetime


class ChatAskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=4_000)
    limit: int = Field(default=5, ge=1, le=20)


class ChatAskResponse(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
