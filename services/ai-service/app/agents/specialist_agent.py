from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.services.specialist_service import SpecialistService


class SpecialistAgent(BaseAgent):
    def __init__(self):
        self.service = SpecialistService()

    async def run(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.service.process(
            query=input_data["query"],
            document_id=input_data.get("document_id"),
            triage_data=input_data.get("triage_data"),
            tool_output=input_data.get("tool_output"),
        )