"""Minimal CLI for testing the assistant without Streamlit.

    python run_cli.py john_doe "recommend sessions"
    python run_cli.py john_doe            # interactive REPL
"""
from __future__ import annotations

import os
import sys

from agent_system.config import get_settings
from agent_system.database.init_db import init_db
from agent_system.graph import run_turn


def _ensure_db() -> None:
    if not os.path.exists(get_settings().db_path):
        init_db()


def _print_turn(username: str, query: str) -> None:
    state = run_turn(username, query)
    print(f"\n[{state.get('intent')} via {state.get('intent_source')}] {state.get('response')}")
    for row in state.get("data", []) or []:
        print(f"   - {row['session_id']}: {row['title']} ({row['time']}, seats {row['seats_left']})")


def main() -> None:
    _ensure_db()
    if len(sys.argv) < 2:
        print("Usage: python run_cli.py <username> [query]")
        raise SystemExit(2)

    username = sys.argv[1]
    if len(sys.argv) >= 3:
        _print_turn(username, " ".join(sys.argv[2:]))
        return

    print(f"Interactive session as '{username}'. Type 'quit' to exit.")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in {"quit", "exit"}:
            break
        if query:
            _print_turn(username, query)


if __name__ == "__main__":
    main()
