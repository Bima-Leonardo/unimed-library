import sqlite3

def connect_db():
    # Membuka/membuat database langsung di dalam server
    conn = sqlite3.connect("digital_library.db")
    return conn
