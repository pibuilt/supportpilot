import json
from typing import Any, Dict

from langchain_core.output_parsers import (
    PydanticOutputParser,
)
from pydantic import Field

from app.prompts.specialist_prompt import SPECIALIST_SYSTEM_PROMPT
from app.schemas.base import (
    SupportPilotBaseModel,
)
from app.services.llm_client import LLMClient


class SpecialistLLMOutput(
    SupportPilotBaseModel
):
    answer: str
    recommendations: list[str] = Field(
        default_factory=list
    )


class SpecialistService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.parser = PydanticOutputParser(
            pydantic_object=SpecialistLLMOutput
        )

    def _extract_supporting_clauses(
        self,
        tool_output: Dict[str, Any] | None,
    ) -> list[Dict[str, Any]]:
        if not tool_output:
            return []

        if tool_output.get("tool") == "retrieval":
            return [
                {
                    "document_id": result.get(
                        "document_id"
                    ),
                    "chunk_id": result.get(
                        "chunk_id"
                    ),
                    "excerpt": result.get(
                        "chunk_text"
                    ),
                    "score": result.get("score"),
                }
                for result in tool_output.get(
                    "results",
                    [],
                )
            ]

        if tool_output.get("tool") == "clause_analysis":
            return tool_output.get(
                "clauses",
                [],
            )

        return []

    async def process(
        self,
        query: str,
        document_id: str | None = None,
        triage_data: Dict[str, Any] | None = None,
        tool_output: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        supporting_clauses = (
            self._extract_supporting_clauses(
                tool_output
            )
        )

        if document_id and not supporting_clauses:
            return {
                "answer": (
                    "I could not access grounded "
                    "document evidence for this "
                    "request, so I cannot safely "
                    "summarize the document."
                ),
                "supporting_clauses": [],
                "recommendations": [
                    "Retry after confirming the "
                    "document is ingested and "
                    "retrieval returned results."
                ],
            }

        tool_context = ""

        if tool_output:
            tool_context = f"""
PRIMARY LEGAL EVIDENCE:
{json.dumps(tool_output, indent=2)}

You MUST base your analysis primarily on this evidence.
Do NOT ignore it.
Do NOT provide generic recommendations.
"""

        prompt = f"""
{SPECIALIST_SYSTEM_PROMPT}

{self.parser.get_format_instructions()}

Triage Data:
{json.dumps(triage_data or {}, indent=2)}

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

        try:
            parsed = self.parser.parse(
                output_text
            )

            return {
                "answer": parsed.answer,
                "supporting_clauses": (
                    supporting_clauses
                ),
                "recommendations": (
                    parsed.recommendations
                ),
            }

        except Exception:
            if supporting_clauses:
                return {
                    "answer": (
                        "I found document evidence, "
                        "but I could not produce a "
                        "safe structured summary "
                        "from it."
                    ),
                    "supporting_clauses": (
                        supporting_clauses
                    ),
                    "recommendations": [],
                }

            return {
                "answer": output_text,
                "supporting_clauses": [],
                "recommendations": [],
            }
