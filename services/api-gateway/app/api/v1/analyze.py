from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import (
    ContractAnalysisRequest,
    ContractAnalysisResponse,
)
from app.services.contract_analysis_service import analyze_contract
from app.utils.response import success_response

router = APIRouter(prefix="/v1", tags=["analysis"])


@router.post(
    "/analyze",
    response_model=dict,
)
def analyze_contract_endpoint(
    payload: ContractAnalysisRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    result = analyze_contract(
        document_id=payload.document_id,
        db=db,
    )

    request_id = getattr(request.state, "request_id", "unknown")
    return success_response(result, request_id)