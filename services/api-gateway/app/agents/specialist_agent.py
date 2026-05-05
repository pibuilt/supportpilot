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
        prompt = SPECIALIST_PROMPT.format(
            context=context,
            query=query,
            format_instructions=self.parser.get_format_instructions(),
        )

        response = self.llm.invoke(prompt)

        parsed = self.parser.parse(response.content)

        return parsed.model_dump()