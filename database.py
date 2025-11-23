import sqlite3

def get_db():
    conn = sqlite3.connect("data/casta.db")
    return conn