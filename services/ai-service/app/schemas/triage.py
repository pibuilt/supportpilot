from pydantic import Field

from app.schemas.base import SupportPilotBaseModel


class TriageRequest(SupportPilotBaseModel):
    query: str = Field(..., min_length=3)
    document_id: str | None = None


class TriageResponse(SupportPilotBaseModel):
    intent: str
    confidence: float
    requires_clarification: bool
    suggested_route: str
    raw_output: str | None = None