from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.db import get_db
from app.shared.deps import get_current_user
from app.threads.schema import (
    ThreadRequest,
    ThreadUpdateRequest,
    ThreadCreationResponse,
    ThreadDetailResponse,
    ThreadUpdateResponse,
    ThreadDeleteResponse,
    ThreadListResponse,
)
from app.threads.service import ThreadService
from app.user.model import User

thread_router = APIRouter(prefix="/threads", tags=["Threads"])


def get_thread_service(
    db: Session = Depends(get_db),
) -> ThreadService:
    return ThreadService(db=db)


@thread_router.post(
    "/create",
    response_model=ThreadCreationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    data: ThreadRequest,
    current_user: User = Depends(get_current_user),
    thread_service: ThreadService = Depends(get_thread_service),
):
    thread = thread_service.create_thread(
        user_id=current_user.id,
        title=data.title,
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread",
        )

    return {
        "success": True,
        "message": "Thread created successfully",
        "data": thread,
    }


@thread_router.get(
    "/{thread_id}",
    response_model=ThreadDetailResponse,
)
def get_thread(
    thread_id: UUID,
    current_user: User = Depends(get_current_user),
    thread_service: ThreadService = Depends(get_thread_service),
):
    thread = thread_service.get_thread_by_id(
        thread_id=thread_id,
        user_id=current_user.id,
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found",
        )

    return {
        "success": True,
        "message": "Thread fetched successfully",
        "data": thread,
    }


@thread_router.patch(
    "/{thread_id}",
    response_model=ThreadUpdateResponse,
)
def update_thread(
    thread_id: UUID,
    data: ThreadUpdateRequest,
    current_user: User = Depends(get_current_user),
    thread_service: ThreadService = Depends(get_thread_service),
):
    thread = thread_service.update_thread(
        thread_id=thread_id,
        user_id=current_user.id,
        title=data.title,
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found",
        )

    return {
        "success": True,
        "message": "Thread updated successfully",
        "data": thread,
    }


@thread_router.delete(
    "/{thread_id}",
    response_model=ThreadDeleteResponse,
)
def delete_thread(
    thread_id: UUID,
    current_user: User = Depends(get_current_user),
    thread_service: ThreadService = Depends(get_thread_service),
):
    deleted = thread_service.delete_thread(
        thread_id=thread_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found",
        )

    return {
        "success": True,
        "message": "Thread deleted successfully",
    }


@thread_router.get(
    "",
    response_model=ThreadListResponse,
)
def get_user_threads(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    thread_service: ThreadService = Depends(get_thread_service),
):
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="limit must be 1-100 and offset must be >= 0",
        )

    threads = thread_service.get_user_threads(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return {
        "success": True,
        "message": "Threads fetched successfully",
        "data": threads,
    }
