from fastapi import APIRouter

from app.schemas.triage import TriageRequest
from app.services.triage_service import TriageService

router = APIRouter(prefix="/v1/triage", tags=["triage"])

service = TriageService()


@router.post("")
async def triage(request: TriageRequest):
    return await service.process(
        query=request.query,
        document_id=request.document_id,
    )