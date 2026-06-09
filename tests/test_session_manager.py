from agent_system.agents import session_manager


def test_get_user(db):
    user = session_manager.get_user("john_doe")
    assert user is not None
    assert user.interests == ["AI", "Data"]
    assert session_manager.get_user("ghost") is None


def test_get_available_sessions_filtered_by_interest(db):
    sessions = session_manager.get_available_sessions(["AI"])
    topics = {s.topic for s in sessions}
    assert topics == {"AI"}
    # S6 (Security, 0 seats) must never appear when filtering AI
    assert all(s.max_seats > 0 for s in sessions)


def test_get_available_sessions_no_filter_returns_all_with_seats(db):
    sessions = session_manager.get_available_sessions()
    ids = {s.session_id for s in sessions}
    assert "S6" not in ids  # full session excluded
    assert "S1" in ids


def test_register_user_decrements_seats_and_blocks_duplicates(db):
    before = session_manager.get_session("S5").max_seats
    assert session_manager.register_user("amir_k", "S5") is True
    after = session_manager.get_session("S5").max_seats
    assert after == before - 1
    # duplicate registration is a no-op
    assert session_manager.register_user("amir_k", "S5") is False
    assert session_manager.get_session("S5").max_seats == after
