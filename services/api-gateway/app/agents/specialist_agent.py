from langchain_core.output_parsers import PydanticOutputParser

from app.prompts.specialist_prompt import SPECIALIST_PROMPT
from app.schemas.specialist import SpecialistOutput
from app.services.llm_factory import get_llm


class SpecialistAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(
            pydantic_object=SpecialistOutput
        )

    def analyze(
        self,
        query: str,
        context: str,
    ) -> dict:
        strict_format_instructions = (
            self.parser.get_format_instructions()
            + "\n\n"
            + 'IMPORTANT: The "risks" field MUST be returned strictly as an array (JSON list) of concise strings. '
              'Do NOT return risks as a single string, paragraph, or any other format.'
        )

        prompt = SPECIALIST_PROMPT.format(
            context=context,
            query=query,
            format_instructions=strict_format_instructions,
        )

        response = self.llm.invoke(prompt)

        try:
            parsed = self.parser.parse(response.content)
        except Exception as e:
            raise ValueError(
                f"Specialist agent parsing failed. Raw output: {response.content}"
            ) from e

        return parsed.model_dump()