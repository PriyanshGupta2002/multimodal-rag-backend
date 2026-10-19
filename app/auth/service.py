# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/auth/service.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 11:06:08 UTC (1792407968)

from sqlalchemy.orm import Session
from app.auth.schema import RegisterRequestSchema, LoginSchema
from app.user.model import User
from sqlalchemy import insert, select
from fastapi import HTTPException, status, Response
from app.shared.helpers import get_password_hash, verify_password, create_token
from app.shared.config import settings
from datetime import timedelta


class AuthService:
    def __init__(self, db: Session, response: Response):
        self.db = db
        self.response = response

    def register_user(self, user: RegisterRequestSchema):
        user_exists_stmt = select(User).where(user.email == User.email)
        existing_user = self.db.execute(user_exists_stmt).scalar_one_or_none()
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )
        else:
            hashed_password = get_password_hash(user.password)
            new_user = User(
                name=user.name, hashed_password=hashed_password, email=user.email
            )
            try:
                self.db.add(new_user)
                self.db.commit()
                self.db.refresh(new_user)
            except Exception:
                self.db.rollback()
                raise
            return new_user

    def _save_token_to_cookies(self, access_token: str, refresh_token: str):
        self.response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )
        self.response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/",
        )

    def login_user(self, user: LoginSchema):
        user_exists_stmt = select(User).where(user.email == User.email)
        existing_user = self.db.execute(user_exists_stmt).scalar_one_or_none()
        if existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        else:
            is_password_correct = verify_password(
                user.password, hashed_password=existing_user.hashed_password
            )
            if not is_password_correct:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect credentials",
                )
            else:
                access_token = create_token(
                    data={"sub": str(existing_user.id), "type": "access"},
                    expires_delta=timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    ),
                )
                refresh_token = create_token(
                    data={"sub": str(existing_user.id), "type": "refresh"},
                    expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                )
                self._save_token_to_cookies(
                    access_token=access_token, refresh_token=refresh_token
                )
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_data": existing_user,
                }
