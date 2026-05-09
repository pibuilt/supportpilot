from app.api.v1.orchestration import router as orchestration_router
from app.api.v1.specialist import router as specialist_router
from app.api.v1.tone import router as tone_router
from app.api.v1.triage import router as triage_router

__all__ = [
    "triage_router",
    "specialist_router",
    "tone_router",
    "orchestration_router",
]