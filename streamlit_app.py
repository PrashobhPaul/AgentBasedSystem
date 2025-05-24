import streamlit as st
from agents.bot_agent import handle_user_query

st.title("Event Management Chatbot")

if 'username' not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    username = st.text_input("Enter your username to continue")
    if st.button("Login"):
        st.session_state.username = username
        st.experimental_rerun()
else:
    st.subheader(f"Welcome {st.session_state.username}!")
    query = st.text_input("Ask about the event or request recommendations:")

    if st.button("Ask") and query:
        response = handle_user_query(st.session_state.username, query)
        st.write(response)

# agents/bot_agent.py
from agents.recommender_agent import recommend_sessions
from agents.session_manager import get_faq_response

STATIC_QUERIES = ["when is the event", "where is the event", "who are the speakers"]

def handle_user_query(user, query):
    lower_query = query.lower()
    for static_q in STATIC_QUERIES:
        if static_q in lower_query:
            return get_faq_response(static_q)
    if "recommend" in lower_query:
        return recommend_sessions(user)
    return "I'm not sure how to help with that yet."

# agents/recommender_agent.py
from utils.db import query_db
from agents.calendar_agent import is_time_free
from agents.session_manager import get_available_sessions, user_registered_sessions

def recommend_sessions(user):
    user_info = query_db("SELECT interests FROM users WHERE username = ?", (user,), one=True)
    if not user_info:
        return "User not found."

    interests = user_info[0].split(',')
    registered = [s[0] for s in user_registered_sessions(user)]
    available_sessions = get_available_sessions(interests)

    recommendations = []
    for session in available_sessions:
        if session[0] in registered:
            continue
        if is_time_free(user, session[3], session[4], session[5]):
            recommendations.append(session)

    if not recommendations:
        return "No sessions available that match your interests and free time."

    return [{"session_id": s[0], "title": s[1], "time": f"{s[3]} {s[4]}-{s[5]}"} for s in recommendations]

# agents/calendar_agent.py
from agents.session_manager import get_user_calendar

def is_time_free(user, day, start, end):
    calendar = get_user_calendar(user)
    if day not in calendar:
        return True
    for slot in calendar[day]:
        if not (end <= slot[0] or start >= slot[1]):
            return False
    return True

# agents/session_manager.py
from utils.db import query_db

def get_faq_response(query):
    faqs = {
        "when is the event": "The event is scheduled across 3 days: June 1st to June 3rd.",
        "where is the event": "The event takes place at the Grand Conference Center, New York.",
        "who are the speakers": "Top industry leaders including Dr. A, Dr. B, and Dr. C."
    }
    return faqs.get(query, "No information available.")

def get_available_sessions(interests):
    placeholders = ','.join('?' for _ in interests)
    query = f"SELECT * FROM sessions WHERE topic IN ({placeholders}) AND max_seats > 0"
    return query_db(query, interests)

def user_registered_sessions(user):
    return query_db("SELECT session_id FROM registrations WHERE username = ?", (user,))

def get_user_calendar(user):
    sessions = query_db("""
        SELECT s.day, s.start_time, s.end_time
        FROM sessions s
        JOIN registrations r ON s.session_id = r.session_id
        WHERE r.username = ?
    """, (user,))
    calendar = {}
    for day, start, end in sessions:
        calendar.setdefault(day, []).append((start, end))
    return calendar
