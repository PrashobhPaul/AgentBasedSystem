import sqlite3

def init_db():
    conn = sqlite3.connect("event.db")
    c = conn.cursor()

    # Drop and recreate tables
    c.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS sessions;
    DROP TABLE IF EXISTS registrations;

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        interests TEXT,
        role TEXT
    );

    CREATE TABLE sessions (
        session_id TEXT PRIMARY KEY,
        title TEXT,
        topic TEXT,
        day TEXT,
        start_time TEXT,
        end_time TEXT,
        speaker TEXT,
        location TEXT,
        max_seats INTEGER
    );

    CREATE TABLE registrations (
        username TEXT,
        session_id TEXT,
        PRIMARY KEY (username, session_id)
    );
    """)

    # Insert dummy users
    users = [
        ("john_doe", "AI,Data", "Manager"),
        ("jane_smith", "Cloud,Security", "Developer")
    ]
    c.executemany("INSERT INTO users VALUES (?, ?, ?)", users)

    # Insert dummy sessions (simplified)
    sessions = [
        ("S1", "AI in Marketing", "AI", "Day 1", "10:00", "11:00", "Dr. A", "Hall A", 50),
        ("S2", "Securing APIs", "Security", "Day 1", "11:00", "12:00", "Dr. B", "Hall B", 50)
    ]
    c.executemany("INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", sessions)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

