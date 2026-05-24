import time

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from app.observability.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
)


class PrometheusMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request,
        call_next,
    ):
        start = time.time()

        response = await call_next(
            request
        )

        duration = (
            time.time() - start
        )

        endpoint = (
            request.url.path
        )

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=endpoint,
        ).observe(duration)

        return response