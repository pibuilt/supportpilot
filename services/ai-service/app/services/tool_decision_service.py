from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.prompts.tool_prompt import TOOL_DECISION_PROMPT
from app.services.llm_client import LLMClient


class ToolDecisionService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.parser = JsonOutputParser()

        self.prompt = PromptTemplate(
            template="""
{system_prompt}

User Query:
{query}
""",
            input_variables=[
                "system_prompt",
                "query",
            ],
        )

    async def decide(
        self,
        query: str,
    ):
        formatted_prompt = self.prompt.format(
            system_prompt=TOOL_DECISION_PROMPT,
            query=query,
        )

        result = await self.llm_client.generate(
            formatted_prompt
        )

        output_text = (
            result["output"]
            if isinstance(result, dict)
            else result
        )

        try:
            parsed = self.parser.parse(
                output_text
            )

            return parsed

        except Exception:
            return {
                "use_tool": False
            }