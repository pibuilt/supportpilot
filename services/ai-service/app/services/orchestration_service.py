import uuid

from app.agents.specialist_agent import SpecialistAgent
from app.agents.tone_agent import ToneAgent
from app.agents.triage_agent import TriageAgent


class OrchestrationService:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.specialist_agent = SpecialistAgent()
        self.tone_agent = ToneAgent()

    async def process(self, query: str, document_id: str | None = None):
        request_id = str(uuid.uuid4())

        triage_result = await self.triage_agent.run(
            {
                "query": query,
                "document_id": document_id,
            }
        )

        specialist_result = await self.specialist_agent.run(
            {
                "query": query,
                "document_id": document_id,
                "triage_data": triage_result,
            }
        )

        tone_result = await self.tone_agent.run(
            {
                "specialist_output": specialist_result,
            }
        )

        return {
            "request_id": request_id,
            "triage": triage_result,
            "specialist": specialist_result,
            "tone": tone_result,
        }