"""Central configuration, sourced from environment variables.

Keeping this in one place makes the system deployable across environments
(local, devcontainer, CI, cloud) without touching code. The LLM settings are
optional: with none of them set, the system runs in pure rule-based mode.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class Settings:
    # Path to the SQLite database file.
    db_path: str = _env("EVENT_DB_PATH", "event.db")

    # Optional LLM layer. Leave LLM_PROVIDER empty for deterministic rule-based
    # intent classification (the default, zero-dependency path).
    # Supported when set: "openai", "azure_openai", "anthropic" (anything
    # langchain's init_chat_model understands).
    llm_provider: str = _env("LLM_PROVIDER")
    llm_model: str = _env("LLM_MODEL", "gpt-4o-mini")

    # Confidence floor below which we ignore the LLM and fall back to rules.
    llm_min_confidence: float = float(_env("LLM_MIN_CONFIDENCE", "0.5"))

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider)


def get_settings() -> Settings:
    """Read settings fresh each call so tests can monkeypatch the environment."""
    return Settings()
