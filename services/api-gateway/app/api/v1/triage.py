from fastapi import APIRouter
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import TriageService

router = APIRouter(prefix="/v1/triage", tags=["triage"])

triage_service = TriageService()


@router.post("", response_model=TriageResponse)
def triage_document(payload: TriageRequest):
    result = triage_service.process(payload.document_text)
    return TriageResponse(**result.dict())