"""Registration action handler.

Validates everything before mutating state: session existence, seat
availability, double-registration, and calendar conflicts. This is the only
place that writes registrations, keeping the side effect well-contained.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agent_system.agents import calendar_agent, session_manager


@dataclass
class RegistrationResult:
    success: bool
    message: str


def register(username: str, session_id: Optional[str]) -> RegistrationResult:
    if not session_id:
        return RegistrationResult(
            False, "Please tell me which session to register for, e.g. 'register for S5'."
        )

    if session_manager.get_user(username) is None:
        return RegistrationResult(False, f"User '{username}' not found.")

    session = session_manager.get_session(session_id)
    if session is None:
        return RegistrationResult(False, f"Session '{session_id}' does not exist.")

    if session_id in set(session_manager.get_registered_session_ids(username)):
        return RegistrationResult(
            False, f"You're already registered for {session_id} ({session.title})."
        )

    if session.max_seats <= 0:
        return RegistrationResult(False, f"Sorry, {session.title} is fully booked.")

    calendar = calendar_agent.build_calendar(username)
    if not calendar_agent.session_fits(calendar, session):
        return RegistrationResult(
            False,
            f"{session.title} clashes with another session on {session.day}.",
        )

    if not session_manager.register_user(username, session_id):
        return RegistrationResult(False, "Could not complete registration, please retry.")

    return RegistrationResult(
        True,
        f"You're registered for {session.title} "
        f"({session.day} {session.start_time}-{session.end_time}, {session.location}).",
    )
