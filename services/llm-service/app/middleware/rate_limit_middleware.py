import os
import time

import redis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0",
)

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


RATE_LIMITS = {
    "/v1/generate": (
        100,
        600,
    ),
    "/v1/embeddings": (
        250,
        600,
    ),
}


class RateLimitMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        path = request.url.path

        matched_limit = None

        for route, limit in RATE_LIMITS.items():
            if path.startswith(route):
                matched_limit = limit
                break

        if not matched_limit:
            return await call_next(
                request
            )

        max_requests, window = (
            matched_limit
        )

        identifier = (
            request.headers.get(
                "x-api-key"
            )
            or request.client.host
        )

        redis_key = (
            f"llm_rolling_rate_limit:{identifier}:{path}"
        )

        now = time.time()

        redis_client.zremrangebyscore(
            redis_key,
            0,
            now - window,
        )

        current_count = (
            redis_client.zcard(
                redis_key
            )
        )

        if (
            current_count
            >= max_requests
        ):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "LLM rate limit exceeded"
                },
            )

        redis_client.zadd(
            redis_key,
            {str(now): now},
        )

        redis_client.expire(
            redis_key,
            window,
        )

        return await call_next(
            request
        )