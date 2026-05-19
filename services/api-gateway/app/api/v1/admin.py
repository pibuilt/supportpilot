from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.constants.audit_events import (
    API_KEY_REGENERATED,
    API_KEY_REVOKED,
    ROLE_CHANGED,
    USER_ACTIVATED,
    USER_SUSPENDED,
)

from app.db.models.api_key import (
    APIKey,
)

from app.db.models.user import (
    User,
)

from app.db.session import get_db

from app.services.admin_service import (
    AdminService,
)

from app.services.audit_service import (
    AuditService,
)

from app.utils.dependencies import (
    get_current_user,
)

from app.utils.rbac import (
    require_admin,
    require_root_admin,
)


router = APIRouter(
    prefix="/v1/admin",
    tags=["Admin"],
)


@router.get("/users")
def list_users(
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_admin(current_user)

    users = (
        db.query(User)
        .filter(
            User.tenant_id
            == current_user["tenant_id"]
        )
        .all()
    )

    return [
        {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
        }
        for user in users
    ]


@router.patch(
    "/users/{user_id}/suspend"
)
def suspend_user(
    user_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_admin(current_user)

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.role == "root_admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot modify root admin",
        )

    if user.id == current_user["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot suspend yourself",
        )

    user.is_active = False

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        event_type=USER_SUSPENDED,
        action="suspend_user",
        status="success",
        resource_type="user",
        resource_id=user.id,
        event_metadata={
            "suspended_email": user.email,
        },
    )

    return {
        "message": "User suspended"
    }


@router.patch(
    "/users/{user_id}/activate"
)
def activate_user(
    user_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_admin(current_user)

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.role == "root_admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot modify root admin",
        )

    user.is_active = True

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        event_type=USER_ACTIVATED,
        action="activate_user",
        status="success",
        resource_type="user",
        resource_id=user.id,
        event_metadata={
            "activated_email": user.email,
        },
    )

    return {
        "message": "User activated"
    }


@router.patch(
    "/users/{user_id}/promote"
)
def promote_user(
    user_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_root_admin(
        current_user
    )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.role == "root_admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot modify root admin",
        )

    AdminService.promote_to_admin(
        user
    )

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        event_type=ROLE_CHANGED,
        action="promote_user",
        status="success",
        resource_type="user",
        resource_id=user.id,
        event_metadata={
            "new_role": "admin",
            "email": user.email,
        },
    )

    return {
        "message": "User promoted to admin"
    }


@router.patch(
    "/users/{user_id}/demote"
)
def demote_user(
    user_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_root_admin(
        current_user
    )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.role == "root_admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot modify root admin",
        )

    if user.id == current_user["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot demote yourself",
        )

    AdminService.demote_to_user(
        user
    )

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        event_type=ROLE_CHANGED,
        action="demote_user",
        status="success",
        resource_type="user",
        resource_id=user.id,
        event_metadata={
            "new_role": "user",
            "email": user.email,
        },
    )

    return {
        "message": "User demoted to user"
    }


@router.patch(
    "/api-keys/{api_key_id}/revoke"
)
def revoke_api_key(
    api_key_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_admin(current_user)

    api_key = (
        db.query(APIKey)
        .filter(
            APIKey.id == api_key_id,
            APIKey.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found",
        )

    AdminService.revoke_api_key(
        api_key
    )

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        api_key_id=api_key.id,
        event_type=API_KEY_REVOKED,
        action="revoke_api_key",
        status="success",
        resource_type="api_key",
        resource_id=api_key.id,
    )

    return {
        "message": "API key revoked"
    }


@router.patch(
    "/api-keys/{api_key_id}/regenerate"
)
def regenerate_api_key(
    api_key_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_admin(current_user)

    api_key = (
        db.query(APIKey)
        .filter(
            APIKey.id == api_key_id,
            APIKey.tenant_id
            == current_user["tenant_id"],
        )
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found",
        )

    new_api_key = (
        AdminService.regenerate_api_key(
            api_key
        )
    )

    db.commit()

    AuditService.log_event(
        db,
        tenant_id=current_user[
            "tenant_id"
        ],
        user_id=current_user[
            "user_id"
        ],
        api_key_id=api_key.id,
        event_type=API_KEY_REGENERATED,
        action="regenerate_api_key",
        status="success",
        resource_type="api_key",
        resource_id=api_key.id,
    )

    return {
        "message": "API key regenerated",
        "new_api_key": new_api_key,
    }