from fastapi import FastAPI, Request
from app.routes.health import router as health_router
from app.middleware.request_context import RequestContextMiddleware
from app.utils.response import error_response

app = FastAPI()

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routes
app.include_router(health_router)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")

    return error_response(
        message="Internal Server Error",
        request_id=request_id,
        status_code=500
    )