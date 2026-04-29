from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.retrieval_service import search_documents

router = APIRouter(prefix="/v1/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
):
    results = search_documents(
        db=db,
        query=payload.query,
        top_k=payload.top_k,
    )

    formatted_results = [
        {
            "document_id": result.document_id,
            "chunk_id": result.chunk_id,
            "score": 1 - result.distance,
        }
        for result in results
    ]

    return {"results": formatted_results}