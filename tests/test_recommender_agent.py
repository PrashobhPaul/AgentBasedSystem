from agent_system.agents import recommender_agent, session_manager


def test_recommend_excludes_conflicts_and_registered(db):
    # john_doe interests = AI, Data; registered for S1 (Day1 10:00-11:00).
    # AI sessions: S1 (registered -> excluded), S5 (Day2 10:00-11:00 -> ok).
    # S3 is Cloud so not an interest match anyway.
    result = recommender_agent.recommend_sessions("john_doe")
    ids = {s.session_id for s in result.sessions}
    assert "S1" not in ids          # already registered
    assert "S5" in ids              # AI, no conflict
    assert "S4" in ids              # Data, Day2 09:00-10:00, no conflict


def test_conflict_filtering_is_real(db):
    # Register john_doe for S5 (Day2 10:00-11:00); then S6 would conflict but is
    # Security (not an interest) and full, so recommendations should shrink.
    session_manager.register_user("john_doe", "S5")
    result = recommender_agent.recommend_sessions("john_doe")
    ids = {s.session_id for s in result.sessions}
    assert "S5" not in ids


def test_unknown_user(db):
    result = recommender_agent.recommend_sessions("nobody")
    assert not result.found
    assert "not found" in result.message.lower()
