# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/auth/router.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-18 13:47:35 UTC (1792331255)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.db import get_db
from app.auth.schema import (
    RegisterRequestSchema,
    RegisterResponseSchema,
    LoginSchema,
    LoginResponse,
)
from app.auth.service import AuthService
from fastapi import Response, Request

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponseSchema,
)
def register_user(
    user: RegisterRequestSchema, response: Response, db: Session = Depends(get_db)
):
    auth_service = AuthService(db=db, response=response)
    registered_user = auth_service.register_user(user=user)
    return {
        "message": "User registered successfully",
        "success": True,
        "data": registered_user,
    }


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=LoginResponse
)
def login_user(user: LoginSchema, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db=db, response=response)
    data = auth_service.login_user(user=user)
    if data is not None:
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "message": "Login Successfull",
            "success": True,
            "data": data["user_data"],
        }


@auth_router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    service = AuthService(db, response)
    return service.refresh_access_token(refresh_token)


@auth_router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
):
    service = AuthService(db, response)
    return service.logout_user()


@auth_router.get("/me")
def get_me(
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db, response=None)
    return service.get_current_user(request)
