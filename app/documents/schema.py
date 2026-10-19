# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/documents/schema.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 16:49:44 UTC (1792428584)

from pydantic import BaseModel, Field
from uuid import UUID


class SearchInDocumentRequest(BaseModel):
    doc_id: UUID
    query: str


class Citation(BaseModel):
    segment_id: str


class FinalStructuredOutput(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
