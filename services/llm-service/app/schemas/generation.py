from pydantic import BaseModel
from typing import Optional


class GenerationRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None


class GenerationResponse(BaseModel):
    output: str