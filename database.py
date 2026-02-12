import sqlite3

DB_FILE = "houses.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS houses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        map_url TEXT,
        owner TEXT,
        size INTEGER,
        status TEXT,
        last_login TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def add(house):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO houses (name, map_url, owner, size, status, last_login)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (house[1], house[2], house[3], house[4], house[5], house[6] if len(house) > 6 else None))
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM houses")
    result = c.fetchall()
    conn.close()
    return result

def clear():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM houses")
    conn.commit()
    conn.close()

def count_houses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM houses")
    result = c.fetchone()[0]
    conn.close()
    return result
