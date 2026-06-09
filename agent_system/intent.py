"""Intent classification.

Two-tier design:
  * ``RuleBasedClassifier`` — deterministic, zero-dependency, always available.
  * ``LLMClassifier``       — optional, provider-agnostic (OpenAI/Azure/Anthropic
                              via langchain). Only used when LLM_PROVIDER is set,
                              and it falls back to rules on low confidence or any
                              error, so the system degrades gracefully.

Intents:  faq | recommend | register | unknown
For ``register`` we also extract a session id (e.g. "S5") as an entity.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol

from agent_system.agents.faq_agent import match_faq_key
from agent_system.config import Settings, get_settings

VALID_INTENTS = {"faq", "recommend", "register", "unknown"}
_SESSION_ID_RE = re.compile(r"\b([sS]\d+)\b")


@dataclass
class Intent:
    name: str
    confidence: float = 1.0
    entities: Dict[str, str] = field(default_factory=dict)
    source: str = "rule"  # "rule" or "llm"


class Classifier(Protocol):
    def classify(self, query: str) -> Intent: ...


def extract_session_id(query: str) -> Optional[str]:
    m = _SESSION_ID_RE.search(query or "")
    return m.group(1).upper() if m else None


class RuleBasedClassifier:
    """Keyword/heuristic intent detection. Deterministic and dependency-free."""

    def classify(self, query: str) -> Intent:
        q = (query or "").lower().strip()

        session_id = extract_session_id(q)
        if "register" in q or "sign up" in q or "book" in q:
            entities = {"session_id": session_id} if session_id else {}
            # "how do I register" is an FAQ, not an action.
            if any(p in q for p in ("how do i", "how to", "how can i")):
                return Intent("faq", 0.9, source="rule")
            return Intent("register", 0.9, entities, source="rule")

        if "recommend" in q or "suggest" in q or "what should i attend" in q:
            return Intent("recommend", 0.9, source="rule")

        if match_faq_key(q) is not None:
            return Intent("faq", 0.8, source="rule")

        return Intent("unknown", 0.4, source="rule")


class LLMClassifier:
    """Optional LLM-backed classifier with a strict JSON contract.

    Provider-agnostic: delegates to langchain's ``init_chat_model`` so the same
    code targets OpenAI, Azure OpenAI, or Anthropic based on env config. Any
    import error, runtime error, or low-confidence answer falls back to rules.
    """

    _SYSTEM = (
        "You are an intent router for an event-management assistant. "
        "Classify the user message into exactly one intent: "
        "'faq', 'recommend', 'register', or 'unknown'. "
        "If intent is 'register', extract the session id (pattern like 'S5'). "
        'Respond ONLY as compact JSON: '
        '{"intent": "...", "confidence": 0.0-1.0, "session_id": "S5 or null"}.'
    )

    def __init__(self, settings: Settings, fallback: RuleBasedClassifier):
        self._settings = settings
        self._fallback = fallback
        self._model = None

    def _get_model(self):
        if self._model is None:
            from langchain.chat_models import init_chat_model  # lazy import

            self._model = init_chat_model(
                self._settings.llm_model, model_provider=self._settings.llm_provider
            )
        return self._model

    def classify(self, query: str) -> Intent:
        import json

        try:
            model = self._get_model()
            resp = model.invoke(
                [("system", self._SYSTEM), ("human", query or "")]
            )
            data = json.loads(getattr(resp, "content", str(resp)))
            name = data.get("intent", "unknown")
            confidence = float(data.get("confidence", 0.0))
            if name not in VALID_INTENTS or confidence < self._settings.llm_min_confidence:
                return self._fallback.classify(query)
            entities = {}
            if name == "register" and data.get("session_id"):
                entities["session_id"] = str(data["session_id"]).upper()
            return Intent(name, confidence, entities, source="llm")
        except Exception:
            # Network/quota/parse failure -> deterministic fallback.
            return self._fallback.classify(query)


def get_classifier(settings: Optional[Settings] = None) -> Classifier:
    settings = settings or get_settings()
    rule = RuleBasedClassifier()
    if settings.llm_enabled:
        return LLMClassifier(settings, fallback=rule)
    return rule
