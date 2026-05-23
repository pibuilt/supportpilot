from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.exceptions import (
    RequestValidationError,
)

from app.routes.health import (
    router as health_router,
)

from app.api.v1.async_test import (
    router as async_test_router,
)

from app.middleware.request_context import (
    RequestContextMiddleware,
)

from app.middleware.auth_middleware import (
    AuthMiddleware,
)

from app.middleware.rate_limit_middleware import (
    RateLimitMiddleware,
)

from app.utils.response import (
    error_response,
)

from app.api.v1.ingestion import (
    router as ingestion_router,
)

from app.api.v1.search import (
    router as search_router,
)

from app.api.v1.analyze import (
    router as analysis_router,
)

from app.api.v1.tickets import (
    router as tickets_router,
)

from app.api.v1.orchestration import (
    router as orchestration_router,
)

from app.api.v1.api_keys import (
    router as api_keys_router,
)

from app.api.v1.auth import (
    router as auth_router,
)

from app.api.v1.admin import (
    router as admin_router,
)

app = FastAPI(
    title="SupportPilot API Gateway",
)

# Middleware
app.add_middleware(
    RequestContextMiddleware,
)

app.add_middleware(
    RateLimitMiddleware,
)

app.add_middleware(
    AuthMiddleware,
)

# Routes
app.include_router(
    health_router,
)

app.include_router(
    async_test_router,
)

app.include_router(
    ingestion_router,
    prefix="/v1",
)

app.include_router(
    search_router,
)

app.include_router(
    analysis_router,
)

app.include_router(
    tickets_router,
)

app.include_router(
    orchestration_router,
)

app.include_router(
    api_keys_router,
)

app.include_router(
    auth_router,
)

app.include_router(
    admin_router,
)

# Global Exception Handler
@app.exception_handler(
    RequestValidationError,
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    return error_response(
        message="Validation Error",
        request_id=request_id,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )