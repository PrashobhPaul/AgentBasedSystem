-- Event Management schema.
-- Times are stored as 'HH:MM' 24h strings; conflict logic compares them as minutes.

CREATE TABLE IF NOT EXISTS users (
    username  TEXT PRIMARY KEY,
    interests TEXT NOT NULL DEFAULT '',   -- comma-separated topics
    role      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    topic      TEXT NOT NULL,
    day        TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time   TEXT NOT NULL,
    speaker    TEXT NOT NULL DEFAULT '',
    location   TEXT NOT NULL DEFAULT '',
    max_seats  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS registrations (
    username   TEXT NOT NULL,
    session_id TEXT NOT NULL,
    PRIMARY KEY (username, session_id),
    FOREIGN KEY (username)   REFERENCES users(username)      ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_topic ON sessions(topic);
CREATE INDEX IF NOT EXISTS idx_registrations_user ON registrations(username);
