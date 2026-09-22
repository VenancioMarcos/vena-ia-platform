from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HumanReviewRequest(StrictModel):
    acknowledgement: Literal[True]
    note: str = Field(min_length=10, max_length=2000)


class HumanReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    result_version: str
    review_state: Literal[
        "REQUIRES_HUMAN_REVIEW", "APPROVED_FOR_CONTROLLED_DOWNLOAD"
    ]
    review_note: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None


class FeedbackCreate(StrictModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    result_id: str
    project_id: str
    result_version: str
    rating: int
    comment: str | None
    created_by: str
    created_at: datetime
