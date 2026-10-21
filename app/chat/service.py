import json
import logging
from collections.abc import Iterator
from uuid import UUID

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.messages.service import MessageService
from app.documents.service import DocumentService
from app.threads.model import Thread

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        db: Session,
        workflow: CompiledStateGraph,
    ):
        self.db = db
        self.workflow = workflow
        self.message_service = MessageService(db)
        self.document_service = DocumentService(db)

    def _get_owned_thread(
        self,
        thread_id: UUID,
        user_id: UUID,
    ) -> Thread | None:
        stmt = select(Thread).where(
            Thread.id == thread_id,
            Thread.user_id == user_id,
            Thread.is_active.is_(True),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _sse(event: str, data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event}\ndata: {payload}\n\n"

    def stream_chat(
        self,
        thread_id: UUID,
        user_id: UUID,
        message: str,
        document_id: UUID,
    ):
        thread = self._get_owned_thread(thread_id, user_id)

        if thread is None:
            yield self._sse(
                "error",
                {"message": "Thread not found or access denied."},
            )
            return

        try:
            self.message_service.create_message(
                thread_id=thread_id,
                role="user",
                content=message,
            )
        except Exception:
            logger.exception("Failed to save user message")
            yield self._sse(
                "error",
                {"message": "Could not save your message."},
            )
            return

        config = {
            "configurable": {
                "thread_id": str(thread_id),
                "document_service": self.document_service,
            }
        }

        inputs = {
            "query": message,
            "user_id": str(user_id),
            "document_id": str(document_id),
            "messages": [HumanMessage(content=message)],
            "retrieved_segments": [],
            "answer": "",
            "usage": {},
            "citations": [],
        }

        final_answer = ""
        final_citations = []
        final_usage = {}

        try:
            yield self._sse("start", {"thread_id": str(thread_id)})

            for mode, data in self.workflow.stream(
                inputs,
                config=config,
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    chunk, metadata = data

                    if metadata.get("langgraph_node") != "generate":
                        continue

                    if getattr(chunk, "type", None) != "AIMessageChunk":
                        continue

                    content = chunk.content

                    if isinstance(content, str) and content:
                        yield self._sse(
                            "token",
                            {"content": content},
                        )

                elif mode == "updates":
                    generate_update = data.get("generate")

                    if generate_update:
                        final_answer = generate_update.get("answer", "")
                        final_citations = generate_update.get("citations", [])
                        final_usage = generate_update.get("usage", {})

            # Save exactly one completed assistant message.
            if final_answer:
                self.message_service.create_message(
                    thread_id=thread_id,
                    role="assistant",
                    content=final_answer,
                    metadata={
                        "citations": final_citations,
                        "usage": final_usage,
                    },
                )

            yield self._sse(
                "citations",
                {"items": final_citations},
            )

            yield self._sse(
                "done",
                {
                    "thread_id": str(thread_id),
                    "saved": bool(final_answer),
                    "usage": final_usage,
                },
            )

        except Exception:
            logger.exception("Workflow streaming failed")
            yield self._sse(
                "error",
                {"message": "Response generation failed."},
            )
