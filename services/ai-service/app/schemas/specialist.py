from typing import Any, Dict, List

from pydantic import Field

from app.schemas.base import SupportPilotBaseModel


class SpecialistRequest(SupportPilotBaseModel):
    query: str = Field(..., min_length=3)
    document_id: str | None = None


class SpecialistResponse(SupportPilotBaseModel):
    answer: str
    supporting_clauses: List[Dict[str, Any]]
    recommendations: List[str]