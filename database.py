import sqlite3
from threading import Lock

lock = Lock()
conn = sqlite3.connect("houses.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS houses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    map TEXT,
    status TEXT,
    size INTEGER,
    owner TEXT,
    last_login TEXT
)
""")
conn.commit()

def add(data):
    with lock:
        c.execute("INSERT INTO houses (name,map,status,size,owner,last_login) VALUES (?,?,?,?,?,?)", data)
        conn.commit()

def get_all():
    with lock:
        c.execute("SELECT * FROM houses")
        return c.fetchall()

def count_houses():
    with lock:
        c.execute("SELECT COUNT(*) FROM houses")
        return c.fetchone()[0]

def clear():
    with lock:
        c.execute("DELETE FROM houses")
        conn.commit()
