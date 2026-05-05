from pydantic import BaseModel

from app.schemas.triage import TriageResponse
from app.schemas.specialist import SpecialistOutput
from app.schemas.tone import ToneOutput


class OrchestrationRequest(BaseModel):
    document_id: str
    query: str


class OrchestrationResponse(BaseModel):
    triage: TriageResponse
    specialist: SpecialistOutput
    tone: ToneOutput