from typing import Any, Dict

from app.prompts.specialist_prompt import SPECIALIST_SYSTEM_PROMPT
from app.services.llm_client import LLMClient


class SpecialistService:
    def __init__(self):
        self.llm_client = LLMClient()

    async def process(
        self,
        query: str,
        document_id: str | None = None,
        triage_data: Dict[str, Any] | None = None,
        tool_output: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        tool_context = ""

        if tool_output:
            tool_context = f"""
PRIMARY LEGAL EVIDENCE:
{tool_output}

You MUST base your analysis primarily on this evidence.
Do NOT ignore it.
Do NOT provide generic recommendations.
"""

        prompt = f"""
{SPECIALIST_SYSTEM_PROMPT}

Triage Data:
{triage_data}

{tool_context}

Query:
{query}
"""

        result = await self.llm_client.generate(prompt)

        output_text = (
            result["output"]
            if isinstance(result, dict)
            else result
        )

        return {
            "answer": output_text,
            "supporting_clauses": [],
            "recommendations": [],
        }