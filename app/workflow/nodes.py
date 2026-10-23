from typing import Any
from uuid import UUID

from langchain_core.runnables import RunnableConfig

from app.workflow.state import RAGState
from app.shared.db import LocalSession
from app.documents.service import DocumentService


def parse_optional_uuid(value: Any) -> UUID | None:
    """Convert a valid UUID string to UUID; treat missing/blank values as None."""
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

    if isinstance(value, UUID):
        return value

    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(
            f"Invalid document_id in workflow state: {value!r}. "
            "Expected a valid UUID string or None."
        ) from exc


def retrieve_node(
    state: RAGState,
    config: RunnableConfig,
) -> dict[str, Any]:
    document_service = config.get("configurable", {}).get("document_service")

    user_id = UUID(str(state["user_id"]))
    document_id = parse_optional_uuid(state.get("document_id"))

    if document_service is not None:
        segments = document_service.semantic_search(
            query=state["query"],
            user_id=user_id,
            top_k=5,
            document_id=document_id,
        )
    else:
        # Studio/local execution: create a database service.
        db = LocalSession()
        try:
            document_service = DocumentService(db)

            segments = document_service.semantic_search(
                query=state["query"],
                user_id=user_id,
                top_k=5,
                document_id=document_id,
            )
        finally:
            db.close()

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
