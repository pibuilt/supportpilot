from fastapi import (
    Depends,
    Header,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.user_auth_service import (
    UserAuthService,
)
from app.utils.security import (
    verify_access_token,
)


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not authorization.startswith(
        "Bearer "
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format",
        )

    token = authorization.replace(
        "Bearer ",
        "",
    )

    payload = verify_access_token(
        token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    service = UserAuthService(
        db
    )

    user = service.get_current_user(
        payload["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user