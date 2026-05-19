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


EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",

    # API key endpoints
    "/v1/api-keys/validate",

    # Auth endpoints
    "/v1/auth/signup",
    "/v1/auth/login",
    "/v1/auth/me",
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

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing API Key"
                },
            )

        db: Session = SessionLocal()

        try:
            auth_service = (
                AuthService(db)
            )

            result = (
                auth_service.validate_api_key(
                    api_key
                )
            )

            if not result["valid"]:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Invalid API Key"
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

            response = await call_next(
                request
            )

            auth_service.log_usage(
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