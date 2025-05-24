import sqlite3

def load_user_data():
    conn = sqlite3.connect("event.db")
    c = conn.cursor()
    c.execute("SELECT username, interests, role FROM users")
    users = {row[0]: {"interests": row[1].split(","), "role": row[2], "calendar": {}, "registered_sessions": []} for row in c.fetchall()}
    conn.close()
    return users
    
def load_faqs():
    return {
        "when is the event": "The event is on 25-27 May 2025.",
        "where is the event": "The event is happening at International Convention Center.",
        "what are the guidelines": "Please carry your badge and follow COVID protocols.",
        "who are the speakers": "We have 20+ speakers from various industries including Dr. A and Dr. B."
    }
