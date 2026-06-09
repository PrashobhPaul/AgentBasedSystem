"""Agent-based Event Management assistant.

Public entry point:

    from agent_system import handle_user_query
    print(handle_user_query("john_doe", "recommend sessions"))
"""
from __future__ import annotations

from agent_system.graph import run_turn


def handle_user_query(username: str, query: str) -> str:
    """Backwards-compatible string API over the LangGraph orchestrator."""
    state = run_turn(username, query)
    return state.get("response", "")


__all__ = ["handle_user_query", "run_turn"]
