from pydantic import BaseModel
from typing import List, Dict, Any


class ContractAnalysisRequest(BaseModel):
    document_id: str


class ClauseFinding(BaseModel):
    clause_type: str
    matched_text: str
    confidence_score: float
    metadata: Dict[str, Any]


class AnalysisSummary(BaseModel):
    total_clauses: int
    by_type: Dict[str, int]


class ContractAnalysisResponse(BaseModel):
    document_id: str
    clauses: List[ClauseFinding]
    summary: AnalysisSummary