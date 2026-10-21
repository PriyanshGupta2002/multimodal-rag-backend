from uuid import UUID

from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session

from app.threads.model import Thread


class ThreadService:
    def __init__(self, db: Session):
        self.db = db

    def create_thread(
        self,
        user_id: UUID,
        title: str = "New Chat",
    ) -> Thread:
        try:
            stmt = insert(Thread).values(user_id=user_id, title=title).returning(Thread)
            thread = self.db.execute(stmt).scalar_one()
            self.db.commit()
            return thread
        except Exception:
            self.db.rollback()
            raise

    def get_thread_by_id(
        self,
        thread_id: UUID,
        user_id: UUID,
    ) -> Thread | None:
        stmt = select(Thread).where(
            Thread.id == thread_id,
            Thread.user_id == user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update_thread(
        self,
        thread_id: UUID,
        user_id: UUID,
        title: str,
    ) -> Thread | None:
        try:
            stmt = (
                update(Thread)
                .where(
                    Thread.id == thread_id,
                    Thread.user_id == user_id,
                )
                .values(title=title)
                .returning(Thread)
            )
            thread = self.db.execute(stmt).scalar_one_or_none()

            if thread is None:
                self.db.rollback()
                return None

            self.db.commit()
            return thread
        except Exception:
            self.db.rollback()
            raise

    def delete_thread(
        self,
        thread_id: UUID,
        user_id: UUID,
    ) -> bool:
        try:
            stmt = (
                delete(Thread)
                .where(
                    Thread.id == thread_id,
                    Thread.user_id == user_id,
                )
                .returning(Thread.id)
            )
            deleted_id = self.db.execute(stmt).scalar_one_or_none()

            if deleted_id is None:
                self.db.rollback()
                return False

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def get_user_threads(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Thread]:
        stmt = (
            select(Thread)
            .where(Thread.user_id == user_id)
            .order_by(Thread.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = self.db.execute(stmt)
        return list(result.scalars().all())
