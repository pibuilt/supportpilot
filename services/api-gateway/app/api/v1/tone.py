from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tone import (
    ToneRequest,
    ToneResponse,
)
from app.services.tone_service import ToneService

router = APIRouter(
    prefix="/v1/tone",
    tags=["tone"],
)

tone_service = ToneService()


@router.post("", response_model=ToneResponse)
def tone_analysis(
    payload: ToneRequest,
    db: Session = Depends(get_db),
):
    result = tone_service.process(
        db=db,
        document_id=payload.document_id,
        query=payload.query,
    )

    return ToneResponse(
        executive_summary=result["executive_summary"],
        business_risks=result["business_risks"],
        recommended_actions=result["recommended_actions"],
    )