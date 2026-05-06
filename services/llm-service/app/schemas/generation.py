from pydantic import BaseModel


class GenerationRequest(BaseModel):
    system_prompt: str
    user_prompt: str

    provider: str = "ollama"
    model: str = "mistral"

    temperature: float = 0.2


class GenerationResponse(BaseModel):
    output: str