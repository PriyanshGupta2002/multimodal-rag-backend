# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/documents/tasks.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 13:30:32 UTC (1792416632)

from app.shared.celery_app import celery_app
from app.shared.db import LocalSession
from app.documents.service import DocumentService


@celery_app.task(name="documents.process_document")
def process_document_task(doc_id: str, user_id: str):
    db = LocalSession()
    try:
        service = DocumentService(db=db)
        service.process_document(doc_id=doc_id, user_id=user_id)
    finally:
        db.close()
