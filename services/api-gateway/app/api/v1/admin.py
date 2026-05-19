from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.constants.audit_events import (
    USER_ACTIVATED,
    USER_SUSPENDED,
)

from app.db.models.user import User

from app.db.session import get_db

from app.services.audit_service import (
    AuditService,
)

from app.utils.dependencies import (
    get_current_user,
)

from app.utils.rbac import (
    require_admin,
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