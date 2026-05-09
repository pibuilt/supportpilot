import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import log_info


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        request.state.request_id = request_id

        response = await call_next(request)

        latency_ms = (time.time() - start_time) * 1000

        log_info(
            message=f"{request.method} {request.url.path}",
            request_id=request_id,
            latency_ms=latency_ms
        )

        response.headers["X-Request-ID"] = request_id
        return response