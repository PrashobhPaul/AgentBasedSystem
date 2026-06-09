"""FAQ knowledge base.

A single, de-duplicated source of FAQ answers (the original project had three
different, contradictory copies of these facts). Matching is keyword-based so
natural phrasings like "where's the venue?" still resolve.
"""
from __future__ import annotations

from typing import Dict, Optional

FAQS: Dict[str, str] = {
    "when": "The event runs across 3 days: Day 1 to Day 3 (25-27 May 2025).",
    "where": "The event takes place at the International Convention Center, New York.",
    "speakers": "Speakers include Dr. A, Dr. B, Dr. C and 20+ industry leaders.",
    "guidelines": "Please carry your badge at all times and follow venue safety protocols.",
    "register": "To register for a session, say e.g. 'register for S5'.",
}

# Keyword triggers mapped to a canonical FAQ key.
_TRIGGERS = {
    "when": ["when", "date", "schedule", "time of the event"],
    "where": ["where", "venue", "location", "place"],
    "speakers": ["speaker", "who is speaking", "presenter"],
    "guidelines": ["guideline", "rule", "badge", "protocol", "covid"],
    "register": ["how do i register", "how to register", "sign up"],
}


def match_faq_key(query: str) -> Optional[str]:
    q = query.lower()
    for key, triggers in _TRIGGERS.items():
        if any(t in q for t in triggers):
            return key
    return None


def get_faq_response(query: str) -> Optional[str]:
    key = match_faq_key(query)
    return FAQS.get(key) if key else None
