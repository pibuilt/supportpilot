from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from sqlalchemy.orm import Session

from app.db.session import (
    SessionLocal,
)
from app.services.auth_service import (
    AuthService,
)
from app.services.user_auth_service import (
    UserAuthService,
)
from app.utils.security import (
    verify_access_token,
)


EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/metrics",

    # API key endpoints
    "/v1/api-keys/validate",

    # Auth endpoints
    "/v1/auth/signup",
    "/v1/auth/login",
    "/v1/auth/me",

    "/test-async",
}


EXCLUDED_PREFIXES = [
    "/v1/admin",
]


class AuthMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if (
            request.url.path
            in EXCLUDED_PATHS
            or any(
                request.url.path.startswith(
                    prefix
                )
                for prefix in EXCLUDED_PREFIXES
            )
        ):
            return await call_next(
                request
            )

        api_key = request.headers.get(
            "x-api-key"
        )
        authorization = request.headers.get(
            "authorization"
        )

        db: Session = SessionLocal()

        try:
            result = None
            auth_mode = None

            if api_key:
                auth_service = (
                    AuthService(db)
                )

                candidate = (
                    auth_service.validate_api_key(
                        api_key
                    )
                )

                if candidate["valid"]:
                    result = candidate
                    auth_mode = "api_key"

            if (
                result is None
                and authorization
                and authorization.startswith(
                    "Bearer "
                )
            ):
                token = authorization.replace(
                    "Bearer ",
                    "",
                )
                payload = (
                    verify_access_token(token)
                )

                if payload:
                    user_service = (
                        UserAuthService(db)
                    )
                    user = (
                        user_service.get_current_user(
                            payload["sub"]
                        )
                    )

                    if user:
                        result = {
                            "valid": True,
                            "owner": user[
                                "full_name"
                            ],
                            "user_id": user[
                                "user_id"
                            ],
                            "role": user[
                                "role"
                            ],
                            "tenant_id": user[
                                "tenant_id"
                            ],
                            "api_key_id": None,
                        }
                        auth_mode = "bearer"

            if result is None:
                detail = (
                    "Invalid API Key"
                    if api_key
                    else "Missing authentication"
                )
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": detail
                    },
                )

            # Legacy compatibility for docs/search/analyze/orchestrate
            request.state.owner = (
                result["owner"]
            )

            # Stable identity for RBAC/quotas/audit
            request.state.user_id = (
                result["user_id"]
            )

            request.state.role = (
                result["role"]
            )

            request.state.tenant_id = (
                result["tenant_id"]
            )

            request.state.api_key_id = (
                result[
                    "api_key_id"
                ]
            )
            request.state.auth_mode = (
                auth_mode
            )

            response = await call_next(
                request
            )

            if result["api_key_id"]:
                AuthService(db).log_usage(
                    api_key_id=result[
                        "api_key_id"
                    ],
                    tenant_id=result[
                        "tenant_id"
                    ],
                    endpoint=request.url.path,
                    status_code=response.status_code,
                    tokens_used=0,
                )

            return response

        finally:
            db.close()
