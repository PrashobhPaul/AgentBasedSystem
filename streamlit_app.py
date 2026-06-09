"""Streamlit UI for the Event Management assistant.

Thin presentation layer over ``agent_system``: it owns session state and
rendering only; all logic lives in the orchestrated agent graph. Auto-initialises
the demo database on first run so the app works out of the box.
"""
from __future__ import annotations

import os

import streamlit as st

from agent_system.config import get_settings
from agent_system.database.init_db import init_db
from agent_system.graph import run_turn

st.set_page_config(page_title="Event Management Assistant", page_icon="🎫")


@st.cache_resource
def _ensure_db() -> str:
    """Seed the demo DB once per server process if it doesn't exist yet."""
    settings = get_settings()
    if not os.path.exists(settings.db_path):
        init_db()
    return settings.db_path


_ensure_db()

st.title("🎫 Event Management Assistant")
st.caption("Ask FAQs, get session recommendations, or register — try `recommend sessions` or `register for S5`.")

if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = []  # list[(role, text)]

# --- Login ---------------------------------------------------------------- #
if not st.session_state.username:
    with st.form("login"):
        username = st.text_input("Enter your username to continue", value="john_doe")
        submitted = st.form_submit_button("Login")
    if submitted and username.strip():
        st.session_state.username = username.strip()
        st.rerun()
    st.info("Demo users: `john_doe`, `jane_smith`, `amir_k`")
    st.stop()

# --- Chat ----------------------------------------------------------------- #
col1, col2 = st.columns([4, 1])
col1.subheader(f"Welcome, {st.session_state.username}!")
if col2.button("Logout"):
    st.session_state.username = None
    st.session_state.history = []
    st.rerun()

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

query = st.chat_input("Ask about the event or request recommendations…")
if query:
    st.session_state.history.append(("user", query))
    with st.chat_message("user"):
        st.markdown(query)

    state = run_turn(st.session_state.username, query)
    response = state.get("response", "")

    with st.chat_message("assistant"):
        st.markdown(response)
        if state.get("data"):
            st.dataframe(state["data"], use_container_width=True, hide_index=True)
        with st.expander("Routing details"):
            st.json(
                {
                    "intent": state.get("intent"),
                    "confidence": state.get("confidence"),
                    "source": state.get("intent_source"),
                    "entities": state.get("entities"),
                }
            )
    st.session_state.history.append(("assistant", response))
