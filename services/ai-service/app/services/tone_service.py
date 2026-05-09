from typing import Any, Dict

from app.prompts.tone_prompt import TONE_SYSTEM_PROMPT
from app.services.llm_client import LLMClient


class ToneService:
    def __init__(self):
        self.llm_client = LLMClient()

    async def process(self, specialist_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
{TONE_SYSTEM_PROMPT}

Specialist Output:
{specialist_output["answer"]}
"""

        result = await self.llm_client.generate(prompt)

        return {
            "final_response": result["output"],
        }