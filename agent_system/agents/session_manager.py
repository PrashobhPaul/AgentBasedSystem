"""Session-domain data access.

All functions return typed models (User/Session) instead of raw tuples, and
every signature is used consistently across the codebase. This module is the
single source of truth for reading/writing session and registration data.
"""
from __future__ import annotations

from typing import List, Optional

from agent_system.models import Session, User
from agent_system.repository.db import execute, fetch_all, fetch_one

_SESSION_COLUMNS = (
    "session_id, title, topic, day, start_time, end_time, speaker, location, max_seats"
)


def get_user(username: str) -> Optional[User]:
    row = fetch_one(
        "SELECT username, interests, role FROM users WHERE username = ?", (username,)
    )
    return User.from_row(tuple(row)) if row else None


def get_session(session_id: str) -> Optional[Session]:
    row = fetch_one(
        f"SELECT {_SESSION_COLUMNS} FROM sessions WHERE session_id = ?", (session_id,)
    )
    return Session.from_row(tuple(row)) if row else None


def get_available_sessions(interests: Optional[List[str]] = None) -> List[Session]:
    """Sessions with seats remaining, optionally filtered by topic interests.

    Passing ``None`` returns every session that still has seats. The original
    code defined this with no arguments while callers passed ``interests`` —
    that mismatch is fixed here with an optional, defaulted parameter.
    """
    if interests:
        placeholders = ",".join("?" for _ in interests)
        rows = fetch_all(
            f"SELECT {_SESSION_COLUMNS} FROM sessions "
            f"WHERE topic IN ({placeholders}) AND max_seats > 0 "
            f"ORDER BY day, start_time",
            tuple(interests),
        )
    else:
        rows = fetch_all(
            f"SELECT {_SESSION_COLUMNS} FROM sessions "
            f"WHERE max_seats > 0 ORDER BY day, start_time"
        )
    return [Session.from_row(tuple(r)) for r in rows]


def get_registered_session_ids(username: str) -> List[str]:
    rows = fetch_all(
        "SELECT session_id FROM registrations WHERE username = ?", (username,)
    )
    return [r["session_id"] for r in rows]


def get_registered_sessions(username: str) -> List[Session]:
    rows = fetch_all(
        f"SELECT {', '.join('s.' + c.strip() for c in _SESSION_COLUMNS.split(','))} "
        "FROM sessions s "
        "JOIN registrations r ON s.session_id = r.session_id "
        "WHERE r.username = ? ORDER BY s.day, s.start_time",
        (username,),
    )
    return [Session.from_row(tuple(r)) for r in rows]


def register_user(username: str, session_id: str) -> bool:
    """Insert a registration and decrement remaining seats atomically.

    Returns True on success. Returns False if the row already exists. Callers
    are expected to have validated seat availability and conflicts first.
    """
    rows = execute(
        "INSERT OR IGNORE INTO registrations (username, session_id) VALUES (?, ?)",
        (username, session_id),
    )
    if rows == 0:
        return False
    execute(
        "UPDATE sessions SET max_seats = max_seats - 1 "
        "WHERE session_id = ? AND max_seats > 0",
        (session_id,),
    )
    return True
