import sqlite3

def get_available_sessions():
    conn = sqlite3.connect("event.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE max_seats > 0")
    sessions = c.fetchall()
    conn.close()
    return sessions

def user_registered(username, session_id):
    conn = sqlite3.connect("event.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM registrations WHERE username = ? AND session_id = ?", (username, session_id))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def get_faq_response(query):
    faq = {
        "when is the event": "The event is on 25-27 May 2025.",
        "where is the event": "International Convention Center.",
        "what are the guidelines": "Carry your badge and follow COVID rules.",
        "who are the speakers": "Top speakers include Dr. A, Dr. B."
    }
    return faq.get(query.lower(), "Sorry, I don’t have that info.")

