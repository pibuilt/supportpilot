from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingestion import DocumentIngestRequest
from app.services.ingestion_service import IngestionService
from app.utils.response import success_response

router = APIRouter()


@router.post("/ingest")
def ingest_document(
    payload: DocumentIngestRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = IngestionService(db)

    owner_id = getattr(request.state, "owner", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    try:
        result = service.ingest_document(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=payload.document_id,
            text=payload.text,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    request_id = getattr(request.state, "request_id", "unknown")

    return success_response(
        result,
        request_id,
    )
