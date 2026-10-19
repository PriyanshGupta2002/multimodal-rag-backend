# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/main.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 10:22:10 UTC (1792405330)

from fastapi import FastAPI
from app.auth.router import auth_router
from app.documents.router import document_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(document_router)
