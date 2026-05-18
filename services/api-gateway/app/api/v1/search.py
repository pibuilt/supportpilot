from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.utils.response import success_response
from app.db.session import get_db
from app.schemas.search import SearchRequest
from app.services.retrieval_service import search_documents
from app.repositories.embedding_repository import (
    EmbeddingRepository,
)

router = APIRouter(
    prefix="/v1",
    tags=["Search"],
)


@router.post("/search")
def semantic_search(
    payload: SearchRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    # Security validation
    if payload.document_id:
        embedding_repo = EmbeddingRepository(
            db
        )

        if not embedding_repo.document_exists_for_owner(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=payload.document_id,
        ):
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

    result = search_documents(
        db=db,
        owner_id=owner_id,
        tenant_id=tenant_id,
        query=payload.query,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )

    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return success_response(
        data=result,
        request_id=request_id,
    )