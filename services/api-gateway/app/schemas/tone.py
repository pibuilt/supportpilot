from pydantic import BaseModel


class ToneRequest(BaseModel):
    document_id: str
    query: str


class ToneResponse(BaseModel):
    executive_summary: str
    business_risks: str
    recommended_actions: str