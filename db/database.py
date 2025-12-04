import sqlite3

DB_PATH = "db/audit_system.db"

def get_connection():
    return sqlite3.connect(DB_PATH)
