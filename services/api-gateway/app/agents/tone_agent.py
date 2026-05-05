from langchain_core.output_parsers import PydanticOutputParser

from app.prompts.tone_prompt import TONE_PROMPT
from app.schemas.tone import ToneOutput
from app.services.llm_factory import get_llm


class ToneAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(
            pydantic_object=ToneOutput
        )

    def refine(
        self,
        summary: str,
        risks: str,
        recommendations: str,
    ) -> dict:
        prompt = TONE_PROMPT.format(
            summary=summary,
            risks=risks,
            recommendations=recommendations,
            format_instructions=self.parser.get_format_instructions(),
        )

        response = self.llm.invoke(prompt)

        parsed = self.parser.parse(response.content)

        return parsed.model_dump()