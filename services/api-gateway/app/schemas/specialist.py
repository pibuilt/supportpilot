from pydantic import BaseModel


class SpecialistRequest(BaseModel):
    document_id: str
    query: str


class SpecialistResponse(BaseModel):
    summary: str
    risks: str
    recommendations: str