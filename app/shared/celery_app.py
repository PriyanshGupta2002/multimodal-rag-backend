# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/shared/celery_app.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 13:30:18 UTC (1792416618)

from celery import Celery
from app.shared.config import settings

celery_app = Celery(
    "multimodal_rag",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.documents.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)
