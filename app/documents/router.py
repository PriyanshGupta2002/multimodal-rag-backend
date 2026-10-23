# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/documents/router.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 16:58:51 UTC (1792429131)

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.shared.db import get_db
from sqlalchemy.orm import Session
from app.documents.service import DocumentService
from app.shared.deps import get_current_user
from app.documents.tasks import process_document_task
from app.documents.schema import SearchInDocumentRequest, DocumentListResponse
from uuid import UUID
from app.user.model import User

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
    if not uploaded_file:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while uploading the document",
        )
    process_document_task.delay(
        str(uploaded_file.id),
        str(user.id),
    )

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


@document_router.get("/status/{doc_id}")
def get_doc_current_status(
    doc_id: UUID,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    document_service = DocumentService(db=db)
    document = document_service.get_document_status(user_id=user.id, doc_id=doc_id)
    return {"status": document.status}


@document_router.get("", response_model=DocumentListResponse)
def get_docs(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    document_service = DocumentService(db=db)
    documents = document_service.get_user_docs(user_id=user.id)
    return DocumentListResponse(total=len(documents), documents=documents)


@document_router.delete("/delete/{doc_id}")
def delete_document(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)

    return service.delete_document(
        document_id=doc_id,
        user_id=current_user.id,
    )
