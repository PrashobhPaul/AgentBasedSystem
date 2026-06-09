"""Thin data-access layer over SQLite.

A single connection helper with row-dict support and a small query API. The
original code opened a new connection in every function and committed on reads;
this centralises connection handling and keeps reads read-only.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, List, Optional

from agent_system.config import get_settings


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(get_settings().db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(query: str, args: Iterable[Any] = ()) -> List[sqlite3.Row]:
    with connection() as conn:
        return conn.execute(query, tuple(args)).fetchall()


def fetch_one(query: str, args: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
    with connection() as conn:
        return conn.execute(query, tuple(args)).fetchone()


def execute(query: str, args: Iterable[Any] = ()) -> int:
    """Run a write statement; returns the number of affected rows."""
    with connection() as conn:
        cur = conn.execute(query, tuple(args))
        conn.commit()
        return cur.rowcount
