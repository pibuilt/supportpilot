from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.specialist import (
    SpecialistRequest,
    SpecialistResponse,
)
from app.services.specialist_service import SpecialistService

router = APIRouter(
    prefix="/v1/specialist",
    tags=["specialist"],
)

specialist_service = SpecialistService()


@router.post("", response_model=SpecialistResponse)
def specialist_analysis(
    payload: SpecialistRequest,
    db: Session = Depends(get_db),
):
    result = specialist_service.process(
        db=db,
        document_id=payload.document_id,
        query=payload.query,
    )

    return SpecialistResponse(
        summary=result,
        risks=result,
        recommendations=result,
    )