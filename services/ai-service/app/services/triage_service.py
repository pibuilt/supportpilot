from typing import Any, Dict

from app.prompts.triage_prompt import TRIAGE_SYSTEM_PROMPT
from app.services.llm_client import LLMClient


class TriageService:
    def __init__(self):
        self.llm_client = LLMClient()

    async def process(self, query: str, document_id: str | None = None) -> Dict[str, Any]:
        prompt = f"""
{TRIAGE_SYSTEM_PROMPT}

User Query:
{query}
"""

        result = await self.llm_client.generate(prompt)

        return {
            "intent": "contract_review",
            "confidence": 0.95,
            "requires_clarification": False,
            "suggested_route": "specialist",
            "raw_output": result,
        }