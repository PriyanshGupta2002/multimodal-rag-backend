from typing import Any
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


class RAGState(MessagesState):
    query: str
    user_id: str
    document_id: str | None
    retrieved_segments: list[dict[str, Any]]
    answer: str
    citations: list[dict[str, Any]]
    usage: dict[str, Any]
