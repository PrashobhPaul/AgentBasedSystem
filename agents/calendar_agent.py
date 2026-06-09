"""Calendar / scheduling logic.

A user's calendar is derived from the sessions they're registered for. The
conflict check compares time windows in minutes (not lexical string compare),
so '9:00' vs '10:00' style inputs are handled correctly.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from agent_system.agents import session_manager
from agent_system.models import Session

# day -> list of (start_minutes, end_minutes)
Calendar = Dict[str, List[Tuple[int, int]]]


def build_calendar(username: str) -> Calendar:
    """Return busy time windows per day, derived from the user's registrations."""
    calendar: Calendar = {}
    for s in session_manager.get_registered_sessions(username):
        calendar.setdefault(s.day, []).append((s.start_minutes, s.end_minutes))
    return calendar


def is_time_free(calendar: Calendar, day: str, start: str, end: str) -> bool:
    """True if [start, end) on ``day`` does not overlap any busy window."""
    from agent_system.models import _to_minutes

    start_m, end_m = _to_minutes(start), _to_minutes(end)
    for slot_start, slot_end in calendar.get(day, []):
        if not (end_m <= slot_start or start_m >= slot_end):
            return False
    return True


def session_fits(calendar: Calendar, session: Session) -> bool:
    return is_time_free(calendar, session.day, session.start_time, session.end_time)
