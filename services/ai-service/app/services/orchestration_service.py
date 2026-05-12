import uuid

from app.agents.specialist_agent import SpecialistAgent
from app.agents.tone_agent import ToneAgent
from app.agents.triage_agent import TriageAgent
from app.services.tool_decision_service import ToolDecisionService
from app.services.tool_service import ToolService


class OrchestrationService:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.specialist_agent = SpecialistAgent()
        self.tone_agent = ToneAgent()

        self.tool_decision_service = ToolDecisionService()
        self.tool_service = ToolService()

    async def process(
        self,
        query: str,
        document_id: str | None = None,
    ):
        request_id = str(uuid.uuid4())

        triage_result = await self.triage_agent.run(
            {
                "query": query,
                "document_id": document_id,
            }
        )

        tool_decision = await self.tool_decision_service.decide(
            query=query,
        )

        tool_output = None

        if (
            tool_decision.get("use_tool")
            and tool_decision.get("tool_call")
        ):
            tool_call = tool_decision["tool_call"]

            tool_output = await self.tool_service.execute_tool(
                tool_name=tool_call["tool_name"],
                **tool_call["arguments"],
            )

        specialist_payload = {
            "query": query,
            "document_id": document_id,
            "triage_data": triage_result,
        }

        if tool_output:
            specialist_payload["tool_output"] = tool_output

        specialist_result = await self.specialist_agent.run(
            specialist_payload
        )

        tone_result = await self.tone_agent.run(
            {
                "specialist_output": specialist_result,
            }
        )

        return {
            "request_id": request_id,
            "triage": triage_result,
            "tool_decision": tool_decision,
            "tool_output": tool_output,
            "specialist": specialist_result,
            "tone": tone_result,
        }