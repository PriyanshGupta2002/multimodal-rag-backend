from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: UUID
    message: str = Field(min_length=1, max_length=10000)
    document_id: UUID | None = None
