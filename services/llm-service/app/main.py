from fastapi import FastAPI

from app.api.v1.generate import router as generate_router
from app.api.v1.embeddings import router as embeddings_router


app = FastAPI(
    title="SupportPilot LLM Service",
    version="0.1.0"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "llm-service"
    }


app.include_router(
    generate_router,
    prefix="/v1"
)

app.include_router(
    embeddings_router,
    prefix="/v1"
)