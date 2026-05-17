from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.embedding_repository import (
    EmbeddingRepository,
)
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
    owner_id = getattr(request.state, "owner", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    embedding_repo = EmbeddingRepository(
        db
    )

    if not embedding_repo.document_exists_for_owner(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=payload.document_id,
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    result = analyze_contract(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=payload.document_id,
        db=db,
    )

    request_id = getattr(request.state, "request_id", "unknown")

    return success_response(
        result,
        request_id,
    )
