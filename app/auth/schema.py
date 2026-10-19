# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/auth/schema.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-18 13:41:47 UTC (1792330907)

from pydantic import BaseModel, EmailStr


class RegisterRequestSchema(BaseModel):
    name: str
    password: str
    email: EmailStr


class RegisteredUserResponse(BaseModel):
    name: str
    email: EmailStr


class RegisterResponseSchema(BaseModel):
    data: RegisteredUserResponse
    message: str
    success: bool


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    success: bool
    message: str
    data: RegisteredUserResponse
