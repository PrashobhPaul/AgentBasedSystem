"""Session recommender.

Pipeline:
  1. Load the user (and their interests).
  2. Pull available sessions matching those interests (seats > 0).
  3. Drop sessions the user is already registered for.
  4. Drop sessions that clash with the user's existing calendar.

The calendar is built from real registration data, so unlike the original code
(which always saw an empty calendar) conflict filtering actually works.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from agent_system.agents import calendar_agent, session_manager
from agent_system.models import Session


@dataclass
class RecommendationResult:
    sessions: List[Session]
    message: str

    @property
    def found(self) -> bool:
        return bool(self.sessions)


def recommend_sessions(username: str) -> RecommendationResult:
    user = session_manager.get_user(username)
    if user is None:
        return RecommendationResult([], f"User '{username}' not found.")

    if not user.interests:
        return RecommendationResult(
            [], "You have no interests on file, so I can't tailor recommendations yet."
        )

    registered = set(session_manager.get_registered_session_ids(username))
    calendar = calendar_agent.build_calendar(username)

    recommended = [
        s
        for s in session_manager.get_available_sessions(user.interests)
        if s.session_id not in registered
        and calendar_agent.session_fits(calendar, s)
    ]

    if not recommended:
        return RecommendationResult(
            [], "No sessions match your interests and free time right now."
        )

    return RecommendationResult(
        recommended,
        f"Found {len(recommended)} session(s) matching your interests "
        f"({', '.join(user.interests)}) that fit your schedule.",
    )
