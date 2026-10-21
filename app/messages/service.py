from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.messages.model import Message


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        thread_id: UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> Message:
        message = Message(
            thread_id=thread_id,
            role=role,
            content=content,
            metadata_=metadata or {},
        )

        try:
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception:
            self.db.rollback()
            raise

    def get_message_by_id(
        self,
        message_id: UUID,
        thread_id: UUID,
    ) -> Message | None:
        stmt = select(Message).where(
            Message.id == message_id,
            Message.thread_id == thread_id,
        )

        return self.db.execute(stmt).scalar_one_or_none()

    def get_thread_messages(
        self,
        thread_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .limit(limit)
            .offset(offset)
        )

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def delete_message(
        self,
        message_id: UUID,
        thread_id: UUID,
    ) -> bool:
        message = self.get_message_by_id(
            message_id=message_id,
            thread_id=thread_id,
        )

        if message is None:
            return False

        try:
            self.db.delete(message)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise
