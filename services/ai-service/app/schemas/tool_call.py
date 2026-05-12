from typing import Any, Dict, Optional

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class ToolDecision(BaseModel):
    use_tool: bool
    tool_call: Optional[ToolCall] = None