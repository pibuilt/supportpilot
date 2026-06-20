from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.orm import (
    Session,
)

from app.db.session import (
    get_db,
)
from app.schemas.base import (
    APIKeyIssueResponse,
    APIKeySummaryResponse,
    APIKeyValidationResponse,
)
from app.services.audit_service import (
    AuditService,
)
from app.services.auth_service import (
    AuthService,
)
from app.services.user_auth_service import (
    UserAuthService,
)
from app.utils.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/v1/api-keys",
    tags=["API Keys"],
)


@router.get(
    "/validate",
    response_model=APIKeyValidationResponse,
)
def validate_api_key(
    x_api_key: str = Header(
        ...
    ),
    db: Session = Depends(
        get_db
    ),
):
    service = AuthService(
        db
    )

    result = (
        service.validate_api_key(
            x_api_key
        )
    )

    if not result["valid"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )

    return result


@router.get(
    "/mine",
    response_model=list[APIKeySummaryResponse],
)
def list_my_api_keys(
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )
    return service.list_user_api_keys(
        current_user["user_id"],
        current_user["tenant_id"],
    )


@router.post(
    "/mine",
    response_model=APIKeyIssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_api_key(
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )
    payload = service.create_additional_api_key(
        current_user["user_id"]
    )
    AuditService.log_event(
        db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        api_key_id=payload["api_key_id"],
        event_type="API_KEY_CREATED",
        action="create_api_key",
        status="success",
        resource_type="api_key",
        resource_id=payload["api_key_id"],
    )
    return payload


@router.patch(
    "/mine/{api_key_id}/revoke"
)
def revoke_my_api_key(
    api_key_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )

    try:
        service.revoke_user_api_key(
            current_user["user_id"],
            current_user["tenant_id"],
            api_key_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    AuditService.log_event(
        db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        api_key_id=api_key_id,
        event_type="API_KEY_REVOKED",
        action="revoke_own_api_key",
        status="success",
        resource_type="api_key",
        resource_id=api_key_id,
    )

    return {
        "message": "API key revoked"
    }


@router.patch(
    "/mine/{api_key_id}/regenerate",
    response_model=APIKeyIssueResponse,
)
def regenerate_my_api_key(
    api_key_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )

    try:
        payload = service.regenerate_user_api_key(
            current_user["user_id"],
            current_user["tenant_id"],
            api_key_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    AuditService.log_event(
        db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        api_key_id=api_key_id,
        event_type="API_KEY_REGENERATED",
        action="regenerate_own_api_key",
        status="success",
        resource_type="api_key",
        resource_id=api_key_id,
    )

    return payload
