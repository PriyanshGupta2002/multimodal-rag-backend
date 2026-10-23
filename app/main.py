# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/main.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 10:22:10 UTC (1792405330)

from fastapi import FastAPI
from app.auth.router import auth_router
from app.documents.router import document_router
from app.threads.router import thread_router
from contextlib import asynccontextmanager
from app.shared.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.workflow.checkpointer import create_checkpointer
from app.workflow.graph import build_workflow
from app.chat.router import chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    with create_checkpointer(settings.DATABASE_URL) as checkpointer:
        app.state.workflow = build_workflow(checkpointer)
        yield


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(thread_router)
app.include_router(chat_router)
