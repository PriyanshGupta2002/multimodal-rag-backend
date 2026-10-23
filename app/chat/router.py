from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.chat.schema import ChatRequest
from app.chat.service import ChatService
from app.shared.db import get_db
from app.shared.deps import get_current_user
from app.workflow.graph import build_workflow
from uuid import UUID
from app.messages.service import MessageService
from app.threads.service import ThreadService

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post("/stream")
def stream_chat(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    workflow = request.app.state.workflow

    chat_service = ChatService(db, workflow=workflow)

    return StreamingResponse(
        chat_service.stream_chat(
            thread_id=payload.thread_id,
            user_id=current_user.id,
            message=payload.message,
            document_id=payload.document_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@chat_router.get("/{thread_id}/messages")
def get_chat_messages(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    thread_service = ThreadService(db)

    thread = thread_service.get_thread_by_id(
        thread_id=thread_id,
        user_id=current_user.id,
    )

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    message_service = MessageService(db)
    messages = message_service.get_thread_messages(thread_id=thread_id)

    return {
        "success": True,
        "message": "Messages fetched successfully",
        "data": [
            {
                "id": str(message.id),
                "thread_id": str(message.thread_id),
                "role": message.role,
                "content": message.content,
                "created_at": (
                    message.created_at.isoformat() if message.created_at else None
                ),
                "metadata": message.metadata_,
            }
            for message in messages
        ],
    }
