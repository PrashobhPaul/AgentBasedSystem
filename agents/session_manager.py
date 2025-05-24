import sqlite3
def get_available_sessions():
    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE max_seats > 0")
    sessions = cursor.fetchall()
    conn.close()
    return sessions
def user_registered(username, session_id):
    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM registrations WHERE username = ? AND session_id = ?", (username, session_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None
def get_faq_response(query):
    faq = {
        "when is the event": "The event is on 25-27 May 2025.",
        "where is the event": "International Convention Center.",
        "what are the guidelines": "Carry your badge and follow COVID rules.",
        "who are the speakers": "Top speakers include Dr. A, Dr. B."
    }
    return faq.get(query.lower(), "Sorry, I don’t have that info.")
def get_user_calendar(username):
    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()
    cursor.execute("SELECT session_id FROM registrations WHERE username = ?", (username,))
    sessions = cursor.fetchall()
    conn.close()
    return [s[0] for s in sessions]

