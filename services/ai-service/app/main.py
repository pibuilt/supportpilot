from fastapi import FastAPI

from app.api.v1.chat import router as chat_router
from app.api.v1.chat_stream import router as chat_stream_router
from app.api.v1.orchestration import router as orchestration_router
from app.api.v1.specialist import router as specialist_router
from app.api.v1.tone import router as tone_router
from app.api.v1.triage import router as triage_router
from app.middleware.request_context import RequestContextMiddleware


app = FastAPI(
    title="SupportPilot AI Service",
    version="1.0.0",
)

app.add_middleware(RequestContextMiddleware)

app.include_router(chat_router)
app.include_router(chat_stream_router)

app.include_router(triage_router)
app.include_router(specialist_router)
app.include_router(tone_router)
app.include_router(orchestration_router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-service",
    }