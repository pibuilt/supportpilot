import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        response = await call_next(request)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "latency_ms": latency_ms,
            },
        )

        response.headers["X-Request-ID"] = request_id

        return response