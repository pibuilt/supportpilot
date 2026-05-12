import json

from app.schemas.tool_call import ToolDecision


def parse_tool_decision(
    raw_output: str,
) -> ToolDecision:
    try:
        cleaned = raw_output.strip()

        data = json.loads(cleaned)

        return ToolDecision(**data)

    except Exception:
        return ToolDecision(
            use_tool=False,
            tool_call=None,
        )