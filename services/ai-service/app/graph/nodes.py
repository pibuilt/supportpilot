from app.agents.specialist_agent import SpecialistAgent
from app.agents.tone_agent import ToneAgent
from app.agents.triage_agent import TriageAgent
from app.graph.state import OrchestrationState
from app.services.tool_decision_service import ToolDecisionService
from app.services.tool_service import ToolService


triage_agent = TriageAgent()
specialist_agent = SpecialistAgent()
tone_agent = ToneAgent()

tool_decision_service = ToolDecisionService()
tool_service = ToolService()


async def triage_node(
    state: OrchestrationState,
):
    triage_result = await triage_agent.run(
        {
            "query": state["query"],
            "document_id": state.get("document_id"),
        }
    )

    state["triage_result"] = triage_result
    return state


async def tool_decision_node(
    state: OrchestrationState,
):
    tool_decision = await tool_decision_service.decide(
        query=state["query"]
    )

    state["tool_decision"] = tool_decision
    return state


async def tool_execution_node(
    state: OrchestrationState,
):
    tool_output = None

    tool_decision = state.get("tool_decision")

    if (
        tool_decision
        and tool_decision.get("use_tool")
        and tool_decision.get("tool_call")
    ):
        tool_call = tool_decision["tool_call"]

        tool_name = tool_call["tool_name"]
        tool_args = dict(
            tool_call["arguments"]
        )

        # Enforce document-scoped retrieval
        if (
            tool_name == "retrieval"
            and state.get("document_id")
        ):
            tool_args["document_id"] = state[
                "document_id"
            ]

        tool_output = await tool_service.execute_tool(
            tool_name=tool_name,
            **tool_args,
        )

    state["tool_output"] = tool_output
    return state


async def specialist_node(
    state: OrchestrationState,
):
    specialist_payload = {
        "query": state["query"],
        "document_id": state.get("document_id"),
        "triage_data": state.get("triage_result"),
    }

    if state.get("tool_output"):
        specialist_payload["tool_output"] = state[
            "tool_output"
        ]

    specialist_result = await specialist_agent.run(
        specialist_payload
    )

    state["specialist_result"] = specialist_result
    return state


async def tone_node(
    state: OrchestrationState,
):
    tone_result = await tone_agent.run(
        {
            "specialist_output": state[
                "specialist_result"
            ]
        }
    )

    state["tone_result"] = tone_result
    return state


def should_use_tools(
    state: OrchestrationState,
):
    tool_decision = state.get("tool_decision")

    if (
        tool_decision
        and tool_decision.get("use_tool")
    ):
        return "tool_execution"

    return "specialist"