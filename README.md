# AgentBasedSystem — Event Management Assistant

A small, production-shaped **agent-based assistant** for a conference/event. A user
can ask FAQs, get **personalised session recommendations** (interest + calendar
aware), and **register** for sessions. Orchestration is built on **LangGraph**;
the underlying agents are **deterministic and rule-based**, with an **optional,
provider-agnostic LLM layer** for fuzzy intent classification that degrades
gracefully to rules when no model is configured.

> This is a ground-up rewrite of the original prototype. It fixes the bugs that
> stopped the old version from running and reorganises the code into clear,
> testable layers. See [What changed](#what-changed-vs-the-original) below.

---

## Architecture

```
                 ┌─────────────────────────────────────────────┐
   user query ──▶│                LangGraph graph              │
                 │                                             │
                 │   classify ──▶ route ─┬─▶ faq ──────┐       │
                 │                       ├─▶ recommend ─┤       │
                 │                       ├─▶ register ──┼──▶ END │
                 │                       └─▶ fallback ──┘       │
                 └─────────────────────────────────────────────┘
                         │
        ┌────────────────┼─────────────────────────────┐
        ▼                ▼                              ▼
   intent layer     domain agents                  data layer
  (rule | LLM)   faq / recommender /            repository + SQLite
                 calendar / registration         (typed models)
```

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Orchestration | `agent_system/graph.py` | LangGraph state machine: classify → route → node → END. In-process fallback if `langgraph` is absent. |
| Intent | `agent_system/intent.py` | Rule-based classifier (default) + optional provider-agnostic `LLMClassifier` with graceful fallback. |
| Agents | `agent_system/agents/*` | `faq_agent`, `recommender_agent`, `calendar_agent`, `registration_agent`, `session_manager`. |
| Data | `agent_system/repository/db.py`, `agent_system/database/*` | Connection handling, schema, seed data. |
| Models | `agent_system/models.py` | `User` / `Session` dataclasses (no more raw tuples). |
| Config | `agent_system/config.py` | Env-driven settings (DB path, LLM provider/model). |
| UI | `streamlit_app.py`, `run_cli.py` | Chat UI and a CLI for quick testing. |

The graph carries a single typed `ConversationState` (username, query, intent,
entities, response, structured `data`) through every node.

---

## Quick start

```bash
pip install -r requirements.txt
python -m agent_system.database.init_db      # create + seed event.db
streamlit run streamlit_app.py               # open http://localhost:8501
```

Or without a browser:

```bash
python run_cli.py john_doe "recommend sessions"
python run_cli.py amir_k   "register for S5"
python run_cli.py john_doe                    # interactive REPL
```

Demo users: `john_doe` (AI, Data), `jane_smith` (Cloud, Security), `amir_k` (AI, Cloud).

---

## Optional LLM layer (provider-agnostic)

By default the assistant runs **100% offline, rule-based** — no API key required.
To route intents with an LLM, set `LLM_PROVIDER` (copy `.env.example` → `.env`):

```bash
export LLM_PROVIDER=openai        # or azure_openai | anthropic
export LLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
pip install langchain-openai      # match the provider you choose
```

The `LLMClassifier` uses LangChain's `init_chat_model`, so the same code targets
OpenAI, Azure OpenAI, or Anthropic. On any error, low confidence
(`LLM_MIN_CONFIDENCE`), or invalid output, it **falls back to the rule-based
classifier** — the system never hard-fails because of the model.

---

## Testing

```bash
pytest
```

27 tests cover calendar conflict math, recommender filtering (interest +
calendar + already-registered), registration guards (full/duplicate/conflict/
missing), intent classification, and full graph routing on an isolated,
per-test seeded database.

---

## What changed vs. the original

The original prototype did not run. Key fixes and improvements:

- **Signature mismatch (crash):** `recommender_agent` called
  `get_available_sessions(interests)` while `session_manager` defined it with
  **no arguments**. Unified into one typed API.
- **Dead conflict logic:** `load_user_data()` always returned an empty calendar
  and empty registrations, so recommendations never accounted for conflicts. The
  calendar is now derived from real registration data.
- **Three contradictory FAQ copies** (different dates/venues across files, plus a
  second implementation pasted as comments inside `streamlit_app.py`) collapsed
  into one source of truth.
- **String time comparison bug:** times were compared lexically; now parsed to
  minutes so `9:30` vs `10:00` behaves correctly.
- **No registration path:** added a guarded `registration_agent` (existence,
  seats, duplicates, conflicts) with atomic seat decrement.
- **Reads committed writes / per-call connections:** centralised data access with
  read-only fetches and a context-managed connection.
- **Added:** LangGraph orchestration, optional LLM intent layer, typed models,
  env config, `requirements.txt`, `.env.example`, seeded demo data (incl.
  registrations), a CLI, a chat-style Streamlit UI, and a pytest suite.

---

## Project layout

```
AgentBasedSystem/
├── streamlit_app.py            # chat UI
├── run_cli.py                  # CLI / REPL
├── requirements.txt
├── .env.example
├── pytest.ini
├── agent_system/
│   ├── config.py  models.py  intent.py  graph.py
│   ├── agents/    faq_agent  recommender_agent  calendar_agent
│   │              registration_agent  session_manager
│   ├── repository/db.py
│   └── database/  schema.sql  init_db.py
└── tests/                      # 27 tests
```
