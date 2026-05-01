from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.utils.response import success_response
from app.db.session import get_db
from app.schemas.search import SearchRequest
from app.services.retrieval_service import search_documents

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
    result = search_documents(
        db=db,
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