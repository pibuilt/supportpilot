from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.services.triage_service import TriageService


class TriageAgent(BaseAgent):
    def __init__(self):
        self.service = TriageService()

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.service.process(
            query=input_data["query"],
            document_id=input_data.get("document_id"),
        )