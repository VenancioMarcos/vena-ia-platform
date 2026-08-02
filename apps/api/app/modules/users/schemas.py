from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class AdminCredentialSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password: str = Field(min_length=12, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str
    created_at: datetime
