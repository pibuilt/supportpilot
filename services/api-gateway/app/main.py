from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from app.routes.health import router as health_router
from app.middleware.request_context import RequestContextMiddleware
from app.utils.response import error_response, success_response
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.search import router as search_router
from app.api.v1.analyze import router as analysis_router
from app.api.v1.tickets import router as tickets_router

app = FastAPI()

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routes
app.include_router(health_router)
app.include_router(ingestion_router, prefix="/v1")
app.include_router(search_router)
app.include_router(analysis_router)
app.include_router(tickets_router)

# Global Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")

    return error_response(
        message="Validation Error",
        request_id=request_id,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )