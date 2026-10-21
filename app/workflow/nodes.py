from typing import Any

from langchain_core.runnables import RunnableConfig
from uuid import UUID
from app.workflow.state import RAGState


def retrieve_node(
    state: RAGState,
    config: RunnableConfig,
) -> dict[str, Any]:
    document_service = config["configurable"]["document_service"]

    segments = document_service.semantic_search(
        query=state["query"],
        user_id=UUID(state["user_id"]),
        top_k=5,
        document_id=(UUID(state["document_id"]) if state.get("document_id") else None),
    )

    return {"retrieved_segments": segments}


def generate_node(
    state: RAGState,
    config: RunnableConfig,
) -> dict[str, Any]:
    document_service = config["configurable"]["document_service"]

    result = document_service.generate_answer_stream(
        query=state["query"],
        retrieved_segments=state["retrieved_segments"],
    )

    return {
        "answer": result["answer"],
        "citations": result["citations"],
        "usage": result["usage"],
    }
