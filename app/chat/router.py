from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.chat.schema import ChatRequest
from app.chat.service import ChatService
from app.shared.db import get_db
from app.shared.deps import get_current_user
from app.workflow.graph import build_workflow

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
