from agent_system import handle_user_query
from agent_system.graph import run_turn


def test_graph_faq(db):
    state = run_turn("john_doe", "where is the event?")
    assert state["intent"] == "faq"
    assert "Convention Center" in state["response"]


def test_graph_recommend_returns_structured_data(db):
    state = run_turn("john_doe", "recommend sessions")
    assert state["intent"] == "recommend"
    assert isinstance(state.get("data"), list)
    assert all("session_id" in row for row in state["data"])


def test_graph_register_flow(db):
    state = run_turn("amir_k", "register for S5")
    assert state["intent"] == "register"
    assert "registered" in state["response"].lower()


def test_graph_fallback(db):
    state = run_turn("john_doe", "tell me a joke")
    assert state["intent"] == "unknown"
    assert "recommend" in state["response"].lower()


def test_string_api_backwards_compatible(db):
    out = handle_user_query("john_doe", "when is the event?")
    assert isinstance(out, str) and out
