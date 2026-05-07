from fastapi import FastAPI

from app.api.v1 import generate, embeddings
from app.middleware.request_context import RequestContextMiddleware
from app.core.logging import configure_logging


configure_logging()

app = FastAPI(
    title="SupportPilot LLM Service",
    version="1.0.0",
)


app.add_middleware(RequestContextMiddleware)


@app.get("/health")
async def health():
    return {"status": "healthy"}


app.include_router(
    generate.router,
    prefix="/v1",
    tags=["generation"],
)

app.include_router(
    embeddings.router,
    prefix="/v1",
    tags=["embeddings"],
)