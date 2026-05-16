from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.base import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyValidationResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/v1/api-keys",
    tags=["API Keys"],
)


@router.post(
    "",
    response_model=APIKeyResponse,
)
def create_api_key(
    request: APIKeyCreateRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.create_api_key(
        owner=request.owner,
        role=request.role,
        tenant_id=request.tenant_id,
    )


@router.get(
    "/validate",
    response_model=APIKeyValidationResponse,
)
def validate_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.validate_api_key(x_api_key)

    if not result["valid"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )

    return result