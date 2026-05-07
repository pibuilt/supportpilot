from pydantic import BaseModel
from typing import List


class ToneRequest(BaseModel):
    document_id: str
    query: str


class ToneResponse(BaseModel):
    executive_summary: str
    business_risks: List[str]
    recommended_actions: str


class ToneOutput(BaseModel):
    executive_summary: str
    business_risks: List[str]
    recommended_actions: str