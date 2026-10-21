from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ThreadRequest(BaseModel):
    title: str = Field(default="New Chat", min_length=1, max_length=300)


class ThreadUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class ThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ThreadCreationResponse(BaseModel):
    success: bool
    message: str
    data: ThreadResponse


class ThreadDetailResponse(BaseModel):
    success: bool
    message: str
    data: ThreadResponse


class ThreadUpdateResponse(BaseModel):
    success: bool
    message: str
    data: ThreadResponse


class ThreadDeleteResponse(BaseModel):
    success: bool
    message: str


class ThreadListResponse(BaseModel):
    success: bool
    message: str
    data: list[ThreadResponse]
