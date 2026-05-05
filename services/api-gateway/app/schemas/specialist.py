from pydantic import BaseModel


class SpecialistRequest(BaseModel):
    document_id: str
    query: str


class SpecialistResponse(BaseModel):
    summary: str
    risks: str
    recommendations: str


class SpecialistOutput(BaseModel):
    summary: str
    risks: str
    recommendations: str