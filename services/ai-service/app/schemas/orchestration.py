from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from pydantic import Field

from app.schemas.base import (
    SupportPilotBaseModel,
)


class OrchestrationRequest(
    SupportPilotBaseModel
):
    owner_id: str
    tenant_id: str
    api_key: str

    query: str = Field(
        ...,
        min_length=3,
    )

    document_id: Optional[
        str
    ] = None

    session_id: Optional[
        str
    ] = None

    context_limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class TriageOutput(
    SupportPilotBaseModel
):
    intent: str
    confidence: float
    requires_clarification: bool
    suggested_route: str


class SpecialistOutput(
    SupportPilotBaseModel
):
    answer: str

    supporting_clauses: List[
        Dict[str, Any]
    ]

    recommendations: List[str]


class ToneOutput(
    SupportPilotBaseModel
):
    final_response: str


class OrchestrationResponse(
    SupportPilotBaseModel
):
    request_id: str
    session_id: str

    triage: TriageOutput

    tool_decision: Optional[
        Dict[str, Any]
    ] = None

    tool_output: Optional[
        Dict[str, Any]
    ] = None

    specialist: SpecialistOutput
    tone: ToneOutput