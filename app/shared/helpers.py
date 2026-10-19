# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/shared/helpers.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-18 13:44:55 UTC (1792331095)

from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.shared.config import settings
from jose import jwt

password_hash = PasswordHash.recommended()


def get_password_hash(password):
    return password_hash.hash(password)


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)
