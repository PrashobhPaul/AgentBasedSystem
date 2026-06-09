"""Initialise and seed the SQLite database.

Run as a module:  python -m agent_system.database.init_db
This creates the schema and loads a small, realistic demo dataset including
registrations (the original seed never populated registrations, which left the
recommender's conflict logic untestable).
"""
from __future__ import annotations

import os
from pathlib import Path

from agent_system.config import get_settings
from agent_system.repository.db import connection

SCHEMA_FILE = Path(__file__).with_name("schema.sql")

USERS = [
    # username, interests, role
    ("john_doe", "AI,Data", "Manager"),
    ("jane_smith", "Cloud,Security", "Developer"),
    ("amir_k", "AI,Cloud", "Architect"),
]

SESSIONS = [
    # id, title, topic, day, start, end, speaker, location, max_seats
    ("S1", "AI in Marketing",        "AI",       "Day 1", "10:00", "11:00", "Dr. A", "Hall A", 50),
    ("S2", "Securing APIs",          "Security", "Day 1", "11:00", "12:00", "Dr. B", "Hall B", 50),
    ("S3", "Scaling on the Cloud",   "Cloud",    "Day 1", "10:30", "11:30", "Dr. C", "Hall C", 2),
    ("S4", "Data Mesh in Practice",  "Data",     "Day 2", "09:00", "10:00", "Dr. D", "Hall A", 40),
    ("S5", "LLM Agents 101",         "AI",       "Day 2", "10:00", "11:00", "Dr. E", "Hall B", 30),
    ("S6", "Zero Trust Networking",  "Security", "Day 2", "10:00", "11:00", "Dr. F", "Hall C", 0),  # full
]

# Pre-existing registrations create a real calendar to test conflicts against.
REGISTRATIONS = [
    ("john_doe", "S1"),   # AI, Day 1 10:00-11:00  -> conflicts with S3 (10:30-11:30)
    ("jane_smith", "S2"), # Security, Day 1 11:00-12:00
]


def init_db(seed: bool = True) -> str:
    settings = get_settings()
    # Start clean so re-runs are deterministic.
    if os.path.exists(settings.db_path):
        os.remove(settings.db_path)

    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    with connection() as conn:
        conn.executescript(schema)
        if seed:
            conn.executemany(
                "INSERT INTO users (username, interests, role) VALUES (?, ?, ?)", USERS
            )
            conn.executemany(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", SESSIONS
            )
            conn.executemany(
                "INSERT INTO registrations (username, session_id) VALUES (?, ?)",
                REGISTRATIONS,
            )
        conn.commit()
    return settings.db_path


if __name__ == "__main__":
    path = init_db()
    print(f"Initialised database at: {path}")
