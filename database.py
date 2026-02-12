import sqlite3
import threading

conn = sqlite3.connect("houses.db", check_same_thread=False)
lock = threading.Lock()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS houses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    map TEXT,
    owner TEXT,
    status TEXT,
    size TEXT,
    player TEXT,
    last_login TEXT
)
""")
conn.commit()

def clear():
    with lock:
        c.execute("DELETE FROM houses")
        conn.commit()

def add(name, map_img, owner, status, size, player, last_login):
    with lock:
        c.execute(
            "INSERT INTO houses (name, map, owner, status, size, player, last_login) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, map_img, owner, status, size, player, last_login)
        )
        conn.commit()

def get_all():
    with lock:
        c.execute("SELECT * FROM houses")
        return c.fetchall()

def count_houses():
    with lock:
        c.execute("SELECT COUNT(*) FROM houses")
        return c.fetchone()[0]
