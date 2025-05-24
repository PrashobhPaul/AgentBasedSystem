import sqlite3

def load_user_data():
    conn = sqlite3.connect("event.db")
    c = conn.cursor()
    c.execute("SELECT username, interests, role FROM users")
    users = {row[0]: {"interests": row[1].split(","), "role": row[2], "calendar": {}, "registered_sessions": []} for row in c.fetchall()}
    conn.close()
    return users
