from agent_system.agents import calendar_agent
from agent_system.models import Session


def test_is_time_free_no_overlap():
    cal = {"Day 1": [(600, 660)]}  # 10:00-11:00
    assert calendar_agent.is_time_free(cal, "Day 1", "11:00", "12:00") is True
    assert calendar_agent.is_time_free(cal, "Day 2", "10:00", "11:00") is True


def test_is_time_free_overlap():
    cal = {"Day 1": [(600, 660)]}  # 10:00-11:00
    assert calendar_agent.is_time_free(cal, "Day 1", "10:30", "11:30") is False
    assert calendar_agent.is_time_free(cal, "Day 1", "09:30", "10:30") is False


def test_adjacent_slots_do_not_conflict():
    cal = {"Day 1": [(600, 660)]}  # 10:00-11:00
    # back-to-back (11:00-12:00) should be free
    assert calendar_agent.is_time_free(cal, "Day 1", "11:00", "12:00") is True


def test_minute_based_comparison_handles_single_digit_hours():
    cal = {"Day 1": [(540, 600)]}  # 09:00-10:00
    s = Session("X", "t", "AI", "Day 1", "9:30", "10:30", "", "", 10)
    # '9:30' must be parsed as 570 min, not string-compared
    assert calendar_agent.session_fits(cal, s) is False


def test_build_calendar_from_registrations(db):
    cal = calendar_agent.build_calendar("john_doe")
    assert "Day 1" in cal
    assert (600, 660) in cal["Day 1"]  # S1 10:00-11:00
