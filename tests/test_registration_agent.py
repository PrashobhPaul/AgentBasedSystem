from agent_system.agents import registration_agent


def test_register_success(db):
    result = registration_agent.register("amir_k", "S5")
    assert result.success is True
    assert "registered" in result.message.lower()


def test_register_missing_session_id(db):
    result = registration_agent.register("amir_k", None)
    assert result.success is False


def test_register_nonexistent_session(db):
    result = registration_agent.register("amir_k", "S999")
    assert result.success is False
    assert "does not exist" in result.message.lower()


def test_register_full_session(db):
    result = registration_agent.register("amir_k", "S6")  # 0 seats
    assert result.success is False
    assert "fully booked" in result.message.lower()


def test_register_conflict(db):
    # john_doe already on S1 (Day1 10:00-11:00); S3 is Day1 10:30-11:30 -> clash.
    result = registration_agent.register("john_doe", "S3")
    assert result.success is False
    assert "clash" in result.message.lower()


def test_double_registration(db):
    assert registration_agent.register("amir_k", "S5").success is True
    second = registration_agent.register("amir_k", "S5")
    assert second.success is False
    assert "already registered" in second.message.lower()
