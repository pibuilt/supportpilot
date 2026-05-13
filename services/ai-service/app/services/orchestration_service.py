import uuid

from app.graph.workflow import build_orchestration_graph


class OrchestrationService:
    def __init__(self):
        self.graph = build_orchestration_graph()

    async def process(
        self,
        query: str,
        document_id: str | None = None,
    ):
        request_id = str(uuid.uuid4())

        initial_state = {
            "query": query,
            "document_id": document_id,
            "request_id": request_id,

            "triage_result": None,
            "tool_decision": None,
            "tool_output": None,
            "specialist_result": None,
            "tone_result": None,
        }

        final_state = await self.graph.ainvoke(
            initial_state
        )

        return {
            "request_id": request_id,
            "triage": final_state.get(
                "triage_result"
            ),
            "tool_decision": final_state.get(
                "tool_decision"
            ),
            "tool_output": final_state.get(
                "tool_output"
            ),
            "specialist": final_state.get(
                "specialist_result"
            ),
            "tone": final_state.get(
                "tone_result"
            ),
        }