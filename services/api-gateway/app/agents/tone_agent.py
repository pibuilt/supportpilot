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
        risks,
        recommendations: str,
    ) -> dict:
        strict_format_instructions = (
            self.parser.get_format_instructions()
            + "\n\n"
            + 'IMPORTANT: The "business_risks" field MUST be returned strictly as an array (JSON list) of concise strings. '
              'Do NOT return business_risks as a paragraph or single string.'
        )

        prompt = TONE_PROMPT.format(
            summary=summary,
            risks=risks,
            recommendations=recommendations,
            format_instructions=strict_format_instructions,
        )

        response = self.llm.invoke(prompt)

        try:
            parsed = self.parser.parse(response.content)
        except Exception as e:
            raise ValueError(
                f"Tone agent parsing failed. Raw output: {response.content}"
            ) from e

        return parsed.model_dump()