"""LangGraph orchestration.

The graph models the assistant as a small state machine:

    classify ──▶ route ──▶ ( faq | recommend | register | fallback ) ──▶ END

State is a typed dict carried through every node. Each node is a pure-ish
function that reads state and returns a partial update. Routing is conditional
on the classified intent. Nodes themselves are deterministic (rule-based);
only the optional classifier may consult an LLM.

If ``langgraph`` is not installed, ``build_app`` raises, but ``run_turn``
provides an equivalent in-process fallback so the rest of the system (and the
tests) never hard-depend on the library being present at runtime.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from agent_system.agents import recommender_agent, registration_agent
from agent_system.agents.faq_agent import get_faq_response
from agent_system.intent import Classifier, get_classifier


class ConversationState(TypedDict, total=False):
    username: str
    query: str
    intent: str
    confidence: float
    intent_source: str
    entities: Dict[str, str]
    response: str
    data: List[Dict[str, Any]]  # structured payload (e.g. recommended sessions)


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def _classify_node(state: ConversationState, classifier: Classifier) -> ConversationState:
    intent = classifier.classify(state.get("query", ""))
    return {
        "intent": intent.name,
        "confidence": intent.confidence,
        "intent_source": intent.source,
        "entities": intent.entities,
    }


def _faq_node(state: ConversationState) -> ConversationState:
    answer = get_faq_response(state.get("query", ""))
    return {"response": answer or "I don't have that information yet."}


def _recommend_node(state: ConversationState) -> ConversationState:
    result = recommender_agent.recommend_sessions(state["username"])
    return {
        "response": result.message,
        "data": [s.as_dict() for s in result.sessions],
    }


def _register_node(state: ConversationState) -> ConversationState:
    session_id = (state.get("entities") or {}).get("session_id")
    result = registration_agent.register(state["username"], session_id)
    return {"response": result.message}


def _fallback_node(state: ConversationState) -> ConversationState:
    return {
        "response": (
            "I can answer event FAQs, recommend sessions, or register you for one. "
            "Try 'recommend sessions' or 'register for S5'."
        )
    }


_NODE_FUNCS = {
    "faq": _faq_node,
    "recommend": _recommend_node,
    "register": _register_node,
    "unknown": _fallback_node,
}


def _route(state: ConversationState) -> str:
    return state.get("intent", "unknown")


# --------------------------------------------------------------------------- #
# Graph construction (LangGraph) with an in-process fallback
# --------------------------------------------------------------------------- #
def build_app(classifier: Optional[Classifier] = None):
    """Compile and return a LangGraph app. Requires ``langgraph``."""
    from langgraph.graph import END, START, StateGraph

    classifier = classifier or get_classifier()
    graph = StateGraph(ConversationState)

    graph.add_node("classify", lambda s: _classify_node(s, classifier))
    for name, func in _NODE_FUNCS.items():
        graph.add_node(name, func)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        _route,
        {"faq": "faq", "recommend": "recommend", "register": "register", "unknown": "unknown"},
    )
    for name in _NODE_FUNCS:
        graph.add_edge(name, END)

    return graph.compile()


def run_turn(
    username: str, query: str, classifier: Optional[Classifier] = None
) -> ConversationState:
    """Run a single conversational turn.

    Uses the compiled LangGraph app when available; otherwise executes the same
    node sequence in-process. Both paths produce identical state, so behavior is
    stable whether or not ``langgraph`` is installed.
    """
    classifier = classifier or get_classifier()
    initial: ConversationState = {"username": username, "query": query}

    try:
        app = build_app(classifier)
        return app.invoke(initial)  # type: ignore[return-value]
    except ImportError:
        # Deterministic fallback mirroring the graph topology.
        state: ConversationState = dict(initial)
        state.update(_classify_node(state, classifier))
        node = _NODE_FUNCS.get(state.get("intent", "unknown"), _fallback_node)
        state.update(node(state))
        return state
