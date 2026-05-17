from typing import (
    Any,
    Dict,
    Optional,
    TypedDict,
    List,
)


class OrchestrationState(
    TypedDict
):
    # Security context
    owner_id: str
    tenant_id: str
    api_key: str

    # Request context
    query: str
    document_id: Optional[
        str
    ]

    # Session context
    session_id: str

    conversation_history: List[
        Dict[str, str]
    ]

    # Workflow outputs
    triage_result: Optional[
        Dict[str, Any]
    ]

    tool_decision: Optional[
        Dict[str, Any]
    ]

    tool_output: Optional[
        Dict[str, Any]
    ]

    specialist_result: Optional[
        Dict[str, Any]
    ]

    tone_result: Optional[
        Dict[str, Any]
    ]

    # Traceability
    request_id: str