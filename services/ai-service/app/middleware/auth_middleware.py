import os
import time

import httpx
import redis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)


API_GATEWAY_VALIDATE_URL = os.getenv(
    "API_GATEWAY_VALIDATE_URL",
    "http://api-gateway:8000/v1/api-keys/validate",
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0",
)

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
}


RATE_LIMITS = {
    "/v1/chat": (
        50,
        600,
    ),
    "/v1/orchestrate": (
        50,
        600,
    ),
    "/v1/triage": (
        100,
        600,
    ),
    "/v1/tools": (
        100,
        600,
    ),
}


class AuthMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        path = request.url.path

        if path in EXCLUDED_PATHS:
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

        matched_limit = None

        for route, limit in RATE_LIMITS.items():
            if path.startswith(route):
                matched_limit = limit
                break

        if matched_limit:
            max_requests, window = (
                matched_limit
            )

            redis_key = (
                f"ai_rolling_rate_limit:{api_key}:{path}"
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
                        "detail": "AI service rate limit exceeded"
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

        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:
            response = await client.get(
                API_GATEWAY_VALIDATE_URL,
                headers={
                    "x-api-key": api_key
                },
            )

        if response.status_code != 200:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid API Key"
                },
            )

        result = response.json()

        request.state.owner = result[
            "owner"
        ]

        request.state.user_id = result[
            "owner"
        ]

        request.state.role = result[
            "role"
        ]

        request.state.tenant_id = result[
            "tenant_id"
        ]

        request.state.api_key = (
            api_key
        )

        return await call_next(
            request
        )