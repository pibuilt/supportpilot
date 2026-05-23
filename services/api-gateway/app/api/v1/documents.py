from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.repositories.document_repository import (
    DocumentRepository,
)


router = APIRouter(
    prefix="/v1/documents",
    tags=["Documents"],
)


@router.get("")
def list_documents(
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = request.state.owner

    tenant_id = (
        request.state.tenant_id
    )

    repo = DocumentRepository(
        db
    )

    documents = (
        repo.list_documents(
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )

    return {
        "items": [
            {
                "document_id": row.document_id,
                "chunk_count": row.chunk_count,
                "embedding_model": row.embedding_model,
                "embedding_version": row.embedding_version,
            }
            for row in documents
        ]
    }


@router.get("/{document_id}")
def get_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = request.state.owner

    tenant_id = (
        request.state.tenant_id
    )

    repo = DocumentRepository(
        db
    )

    chunks = repo.get_document(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=document_id,
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    first = chunks[0]

    return {
        "document_id": document_id,
        "chunk_count": len(
            chunks
        ),
        "embedding_model": (
            first.embedding_model
        ),
        "embedding_version": (
            first.embedding_version
        ),
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "chunk_text": (
                    chunk.chunk_text
                ),
            }
            for chunk in chunks
        ],
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = request.state.owner

    tenant_id = (
        request.state.tenant_id
    )

    repo = DocumentRepository(
        db
    )

    deleted = repo.delete_document(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=document_id,
    )

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "document_id": document_id,
        "deleted_chunks": deleted,
    }