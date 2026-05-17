from typing import Any, Dict

from langchain_core.output_parsers import (
    PydanticOutputParser,
)

from app.prompts.tone_prompt import TONE_SYSTEM_PROMPT
from app.schemas.tone import ToneResponse
from app.services.llm_client import LLMClient


class ToneService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.parser = PydanticOutputParser(
            pydantic_object=ToneResponse
        )

    async def process(
        self,
        specialist_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        specialist_answer = specialist_output[
            "answer"
        ]

        if specialist_output.get(
            "supporting_clauses"
        ):
            return {
                "final_response": (
                    specialist_answer
                )
            }

        prompt = f"""
{TONE_SYSTEM_PROMPT}

{self.parser.get_format_instructions()}

Specialist Output:
{specialist_answer}
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
                "final_response": (
                    parsed.final_response
                ),
            }

        except Exception:
            return {
                "final_response": (
                    specialist_answer
                ),
            }
