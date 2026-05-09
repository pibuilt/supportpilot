from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.services.tone_service import ToneService


class ToneAgent(BaseAgent):
    def __init__(self):
        self.service = ToneService()

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.service.process(
            specialist_output=input_data["specialist_output"]
        )