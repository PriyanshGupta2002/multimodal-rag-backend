# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/shared/deps.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 10:25:36 UTC (1792405536)

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.db import get_db
from jose import jwt
from app.user.model import User
from app.shared.config import settings


def get_current_user(
    access_token: str | None = Cookie(default=None), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if access_token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "access":
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    else:
        return user
