from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    should_use_tools,
    specialist_node,
    tone_node,
    tool_decision_node,
    tool_execution_node,
    triage_node,
)
from app.graph.state import OrchestrationState


def build_orchestration_graph():
    workflow = StateGraph(
        OrchestrationState
    )

    workflow.add_node(
        "triage",
        triage_node,
    )

    workflow.add_node(
        "tool_decision",
        tool_decision_node,
    )

    workflow.add_node(
        "tool_execution",
        tool_execution_node,
    )

    workflow.add_node(
        "specialist",
        specialist_node,
    )

    workflow.add_node(
        "tone",
        tone_node,
    )

    workflow.add_edge(
        START,
        "triage",
    )

    workflow.add_edge(
        "triage",
        "tool_decision",
    )

    workflow.add_conditional_edges(
        "tool_decision",
        should_use_tools,
        {
            "tool_execution": "tool_execution",
            "specialist": "specialist",
        },
    )

    workflow.add_edge(
        "tool_execution",
        "specialist",
    )

    workflow.add_edge(
        "specialist",
        "tone",
    )

    workflow.add_edge(
        "tone",
        END,
    )

    return workflow.compile()