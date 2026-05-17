from typing import Any, Dict

from langchain_core.output_parsers import (
    PydanticOutputParser,
)

from app.prompts.triage_prompt import TRIAGE_SYSTEM_PROMPT
from app.schemas.triage import (
    TriageResponse,
)
from app.services.llm_client import LLMClient


class TriageService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.parser = PydanticOutputParser(
            pydantic_object=TriageResponse
        )

    async def process(
        self,
        query: str,
        document_id: str | None = None,
    ) -> Dict[str, Any]:
        prompt = f"""
{TRIAGE_SYSTEM_PROMPT}

{self.parser.get_format_instructions()}

Document Context:
{"Document-specific request" if document_id else "No document id provided"}

User Query:
{query}
"""

        result = await self.llm_client.generate(prompt)

        output_text = (
            result["output"]
            if isinstance(result, dict)
            else result
        )

        try:
            parsed = self.parser.parse(
                output_text
            )

            triage = parsed.model_dump()
            triage["raw_output"] = output_text

            return triage

        except Exception:
            return {
                "intent": "contract_review",
                "confidence": 0.95,
                "requires_clarification": False,
                "suggested_route": "specialist",
                "raw_output": output_text,
            }
