from langgraph.graph import END, StateGraph

from app.rag.nodes import (
    clarify_node,
    classify_intent_node,
    fallback_node,
    generate_node,
    grade_documents_node,
    retrieve_node,
)
from app.rag.state import RAGState


def _route_by_intent(state: RAGState) -> str:
    intent = state.get("intent")
    if intent == "transito":
        return "retrieve"
    if intent == "saludo":
        return "retrieve"
    if intent == "vaga":
        return "clarify"
    return "fallback"


def _should_generate(state: RAGState) -> str:
    return "generate" if not state.get("fallback") else "fallback"


def _build_workflow() -> StateGraph:
    workflow = StateGraph(RAGState)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("clarify", clarify_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_documents_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("fallback", fallback_node)

    workflow.set_entry_point("classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        _route_by_intent,
        {
            "retrieve": "retrieve",
            "clarify": "clarify",
            "fallback": "fallback",
        },
    )
    workflow.add_edge("clarify", END)
    workflow.add_edge("retrieve", "grade")
    workflow.add_conditional_edges(
        "grade",
        _should_generate,
        {"generate": "generate", "fallback": "fallback"},
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("fallback", END)
    return workflow


def get_rag_graph(checkpointer):
    workflow = _build_workflow()
    return workflow.compile(checkpointer=checkpointer)
