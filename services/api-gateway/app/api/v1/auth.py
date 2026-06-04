from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from sqlalchemy.orm import (
    Session,
)

from app.db.session import (
    get_db,
)
from app.schemas.auth import (
    AuthTokenResponse,
    CurrentUserResponse,
    UserLoginRequest,
    UserSignupRequest,
)
from app.services.user_auth_service import (
    UserAuthService,
)
from app.utils.security import (
    verify_access_token,
)


router = APIRouter(
    prefix="/v1/auth",
    tags=["Auth"],
)


@router.post(
    "/signup",
    response_model=AuthTokenResponse,
)
def signup(
    request: UserSignupRequest,
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )

    try:
        return service.signup(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            tenant_id=request.tenant_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(
        get_db
    ),
):
    service = UserAuthService(
        db
    )

    try:
        return service.login(
            email=request.email,
            password=request.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_current_user(
    authorization: str = Header(
        ...
    ),
    db: Session = Depends(
        get_db
    ),
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