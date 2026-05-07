from pydantic import BaseModel
from typing import List


class SpecialistRequest(BaseModel):
    document_id: str
    query: str


class SpecialistResponse(BaseModel):
    summary: str
    risks: List[str]
    recommendations: str


class SpecialistOutput(BaseModel):
    summary: str
    risks: List[str]
    recommendations: str