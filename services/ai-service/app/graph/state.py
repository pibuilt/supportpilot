from typing import Any, Dict, Optional, TypedDict


class OrchestrationState(TypedDict):
    query: str
    document_id: Optional[str]

    triage_result: Optional[Dict[str, Any]]
    tool_decision: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]

    specialist_result: Optional[Dict[str, Any]]
    tone_result: Optional[Dict[str, Any]]

    request_id: str