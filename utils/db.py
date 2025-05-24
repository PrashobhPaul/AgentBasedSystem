import sqlite3

def get_connection():
    return sqlite3.connect("event.db")

def query_db(query, args=(), one=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

