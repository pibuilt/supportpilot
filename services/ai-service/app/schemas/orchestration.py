from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import SupportPilotBaseModel


class OrchestrationRequest(SupportPilotBaseModel):
    query: str = Field(..., min_length=3)
    document_id: Optional[str] = None
    context_limit: int = Field(default=5, ge=1, le=20)


class TriageOutput(SupportPilotBaseModel):
    intent: str
    confidence: float
    requires_clarification: bool
    suggested_route: str


class SpecialistOutput(SupportPilotBaseModel):
    answer: str
    supporting_clauses: List[Dict[str, Any]]
    recommendations: List[str]


class ToneOutput(SupportPilotBaseModel):
    final_response: str


class OrchestrationResponse(SupportPilotBaseModel):
    request_id: str
    triage: TriageOutput
    specialist: SpecialistOutput
    tone: ToneOutput