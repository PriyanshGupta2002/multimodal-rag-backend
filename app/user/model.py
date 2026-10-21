# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/user/model.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 09:02:48 UTC (1792400568)

from sqlalchemy import String, Uuid
from app.shared.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    threads = relationship(
        "Thread", back_populates="user", cascade="all, delete-orphan"
    )
