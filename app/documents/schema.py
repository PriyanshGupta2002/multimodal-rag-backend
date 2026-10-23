# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/documents/schema.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 16:49:44 UTC (1792428584)

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class SearchInDocumentRequest(BaseModel):
    doc_id: UUID
    query: str


class Citation(BaseModel):
    segment_id: str


class FinalStructuredOutput(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)


class DocumentSchema(BaseModel):
    id: UUID
    filename: str
    file_url: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: list[DocumentSchema]
    total: int
