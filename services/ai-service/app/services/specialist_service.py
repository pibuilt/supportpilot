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
    ) -> Dict[str, Any]:
        prompt = f"""
{SPECIALIST_SYSTEM_PROMPT}

Query:
{query}
"""

        result = await self.llm_client.generate(prompt)

        return {
            "answer": result["output"],
            "supporting_clauses": [],
            "recommendations": [],
        }