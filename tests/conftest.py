"""Shared test fixtures.

Each test gets an isolated, freshly-seeded SQLite database via a temp file and
an EVENT_DB_PATH override, so tests never touch the developer's real event.db.
"""
from __future__ import annotations

import pytest

from agent_system.database.init_db import init_db


@pytest.fixture()
def db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_event.db"
    monkeypatch.setenv("EVENT_DB_PATH", str(db_path))
    # Ensure no LLM is configured during tests -> deterministic rule-based path.
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    init_db()
    return str(db_path)
