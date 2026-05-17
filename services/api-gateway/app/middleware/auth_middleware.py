from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.auth_service import AuthService


EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/v1/api-keys",
    "/v1/auth/signup",
    "/v1/auth/login",
    "/v1/auth/me",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        api_key = request.headers.get("x-api-key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing API Key",
                },
            )

        db: Session = SessionLocal()

        try:
            auth_service = AuthService(db)
            result = auth_service.validate_api_key(api_key)

            if not result["valid"]:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Invalid API Key",
                    },
                )

            request.state.owner = result["owner"]
            request.state.user_id = result["owner"]
            request.state.role = result["role"]
            request.state.tenant_id = result["tenant_id"]

        finally:
            db.close()

        return await call_next(request)