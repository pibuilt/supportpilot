from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from app.routes.health import router as health_router
from app.middleware.request_context import RequestContextMiddleware
from app.utils.response import error_response

app = FastAPI()

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routes
app.include_router(health_router)


# Global Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")

    return error_response(
        message="Validation Error",
        request_id=request_id,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )