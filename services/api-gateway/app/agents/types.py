from pydantic import BaseModel
from typing import List


class AgentResult(BaseModel):
    document_type: str
    legal_area: str
    risk_level: str
    confidence_score: float
    recommended_agent: str
    clarification_needed: bool
    clarification_questions: List[str]