import sqlite3
import os

DB_FILE = "houses.db"

# Tworzenie tabeli jeśli nie istnieje
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS houses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            map_url TEXT,
            size INTEGER,
            owner TEXT,
            last_login TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def clear():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM houses")
    conn.commit()
    conn.close()

def add(house):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO houses (name, map_url, size, owner, last_login)
        VALUES (?, ?, ?, ?, ?)
    ''', (house["name"], house["map_url"], house["size"], house["owner"], house["last_login"]))
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, map_url, size, owner, last_login FROM houses")
    rows = c.fetchall()
    conn.close()
    return rows

def count_houses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM houses")
    n = c.fetchone()[0]
    conn.close()
    return n
