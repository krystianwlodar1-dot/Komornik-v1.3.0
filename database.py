import sqlite3

DB_FILE = "houses.db"

def connect():
    return sqlite3.connect(DB_FILE)

def create_table():
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS houses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                map_url TEXT,
                owner TEXT,
                size INTEGER,
                status TEXT,
                last_login TEXT
            )
        """)
        conn.commit()

def clear():
    with connect() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM houses")
        conn.commit()

def add(house):
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO houses (address, map_url, owner, size, status, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        """, house)
        conn.commit()

def get_all():
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM houses")
        return c.fetchall()

def count_houses():
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM houses")
        return c.fetchone()[0]

create_table()
