import uuid

from app.graph.workflow import build_orchestration_graph
from app.services.memory_service import MemoryService
from app.graph.checkpoint import GraphCheckpointService


class OrchestrationService:
    def __init__(self):
        self.graph = build_orchestration_graph()
        self.memory_service = MemoryService()
        self.checkpoint_service = GraphCheckpointService()

    async def process(
        self,
        query: str,
        document_id: str | None = None,
        session_id: str | None = None,
    ):
        request_id = str(uuid.uuid4())

        session_id = session_id or str(uuid.uuid4())

        conversation_history = self.memory_service.load_session(
            session_id
        )

        initial_state = {
            "query": query,
            "document_id": document_id,

            "session_id": session_id,
            "conversation_history": conversation_history,

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

        final_response = (
            final_state.get("tone_result", {})
            .get("final_response", "")
        )

        self.memory_service.append_message(
            session_id,
            "user",
            query,
        )

        self.memory_service.append_message(
            session_id,
            "assistant",
            final_response,
        )

        self.checkpoint_service.save_checkpoint(
            session_id,
            final_state,
        )

        return {
            "request_id": request_id,
            "session_id": session_id,

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