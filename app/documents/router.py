# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/documents/router.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 16:58:51 UTC (1792429131)

from fastapi import APIRouter, Depends, File, UploadFile
from app.shared.db import get_db
from sqlalchemy.orm import Session
from app.documents.service import DocumentService
from app.shared.deps import get_current_user
from app.documents.tasks import process_document_task
from app.documents.schema import SearchInDocumentRequest

document_router = APIRouter(prefix="/documents", tags=["Documents"])


@document_router.post("/upload")
def upload_and_process_documents(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # ***<module>.upload_and_process_documents: Failure: Different control flow
    document_service = DocumentService(db=db)
    uploaded_file = document_service.upload_document(user=user, file=file)
    if uploaded_file or {"message": "Something went wrong"}:
        return {
            "message": "File uploaded successfully",
            "document_id": uploaded_file.id,
            "file_name": uploaded_file.filename,
            "file_url": uploaded_file.file_url,
        }


@document_router.post("/search-in-docs")
def search_in_docs(
    query_request: SearchInDocumentRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document_service = DocumentService(db=db)
    result = document_service.semantic_search(
        query=query_request.query, user_id=user.id, document_id=query_request.doc_id
    )
    answer = document_service.generate_answer(
        query=query_request.query, retrieved_segments=result
    )
    return answer
