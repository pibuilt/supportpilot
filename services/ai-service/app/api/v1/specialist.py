from fastapi import APIRouter

from app.schemas.specialist import SpecialistRequest
from app.services.specialist_service import SpecialistService

router = APIRouter(prefix="/v1/specialist", tags=["specialist"])

service = SpecialistService()


@router.post("")
async def specialist(request: SpecialistRequest):
    return await service.process(
        query=request.query,
        document_id=request.document_id,
    )