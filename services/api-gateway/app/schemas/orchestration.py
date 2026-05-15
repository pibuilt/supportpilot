from typing import Optional

from pydantic import BaseModel, Field


class OrchestrationRequest(
    BaseModel
):
    query: str = Field(
        ...,
        min_length=3,
    )

    document_id: Optional[str] = None

    session_id: Optional[str] = None

    context_limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class OrchestrationResponse(
    BaseModel
):
    request_id: str
    session_id: str

    triage: dict
    tool_decision: dict | None = None
    tool_output: dict | None = None
    specialist: dict
    tone: dict