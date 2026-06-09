"""Typed domain models.

Plain dataclasses keep the data layer explicit and decouple the rest of the
system from raw SQLite tuples (the original code passed positional tuples
around, which is where most of its bugs came from).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


def _to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes since midnight for safe comparison."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass(frozen=True)
class User:
    username: str
    interests: List[str] = field(default_factory=list)
    role: str = ""

    @staticmethod
    def from_row(row) -> "User":
        username, interests, role = row
        parsed = [i.strip() for i in (interests or "").split(",") if i.strip()]
        return User(username=username, interests=parsed, role=role or "")


@dataclass(frozen=True)
class Session:
    session_id: str
    title: str
    topic: str
    day: str
    start_time: str
    end_time: str
    speaker: str
    location: str
    max_seats: int

    @property
    def start_minutes(self) -> int:
        return _to_minutes(self.start_time)

    @property
    def end_minutes(self) -> int:
        return _to_minutes(self.end_time)

    def overlaps(self, day: str, start: str, end: str) -> bool:
        """True if this session collides in time with the given window."""
        if self.day != day:
            return False
        return not (
            self.end_minutes <= _to_minutes(start)
            or self.start_minutes >= _to_minutes(end)
        )

    @staticmethod
    def from_row(row) -> "Session":
        return Session(*row)

    def as_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "topic": self.topic,
            "day": self.day,
            "time": f"{self.day} {self.start_time}-{self.end_time}",
            "speaker": self.speaker,
            "location": self.location,
            "seats_left": self.max_seats,
        }
