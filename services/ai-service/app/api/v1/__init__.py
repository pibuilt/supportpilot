from app.api.v1.chat import router as chat_router
from app.api.v1.chat_stream import router as chat_stream_router
from app.api.v1.orchestration import router as orchestration_router
from app.api.v1.specialist import router as specialist_router
from app.api.v1.tone import router as tone_router
from app.api.v1.triage import router as triage_router

__all__ = [
    "chat_router",
    "chat_stream_router",
    "triage_router",
    "specialist_router",
    "tone_router",
    "orchestration_router",
]