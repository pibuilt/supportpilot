from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingestion import DocumentIngestRequest
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/ingest")
def ingest_document(
    payload: DocumentIngestRequest,
    db: Session = Depends(get_db),
):
    service = IngestionService(db)

    return service.ingest_document(
        document_id=payload.document_id,
        text=payload.text,
    )