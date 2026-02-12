import sqlite3
from datetime import datetime

DB_FILE = "houses.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Tworzenie tabeli jeśli nie istnieje
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

def add(house):
    """Dodaje domek do bazy"""
    c.execute("""
    INSERT INTO houses (name, map_url, owner, size, status, last_login)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (house[1], house[2], house[3], house[4], house[5], house[6] if len(house) > 6 else None))
    conn.commit()

def get_all():
    """Zwraca wszystkie domki"""
    c.execute("SELECT * FROM houses")
    return c.fetchall()

def clear():
    """Czyści tabelę domków"""
    c.execute("DELETE FROM houses")
    conn.commit()

def count_houses():
    c.execute("SELECT COUNT(*) FROM houses")
    return c.fetchone()[0]
