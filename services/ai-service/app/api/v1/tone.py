from fastapi import APIRouter

from app.schemas.tone import ToneRequest
from app.services.tone_service import ToneService

router = APIRouter(prefix="/v1/tone", tags=["tone"])

service = ToneService()


@router.post("")
async def tone(request: ToneRequest):
    return await service.process(
        specialist_output={
            "answer": request.answer,
        },
    )