# db.py
import sqlite3

class Database:
    """One shared connection object for the whole app."""

    def __init__(self, path="object.db"):
        self.path = path
        self.conn = None
        self.cursor = None

    def connect(self):
        # Added check_same_thread=False to fix the Flask multi-thread error
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        
        self.conn.row_factory = sqlite3.Row        # rows behave like dicts
        self.conn.execute("PRAGMA foreign_keys = ON;")  # enforce FK
        self.cursor = self.conn.cursor()
        print(f"[DB] Connected to {self.path}")

    def close(self):
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS student (
                id    TEXT PRIMARY KEY,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                UNIQUE (fname, lname)
            );

            CREATE TABLE IF NOT EXISTS report (
                id         TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                title      TEXT NOT NULL,
                type       TEXT NOT NULL,
                UNIQUE (student_id, title, type),
                FOREIGN KEY (student_id) REFERENCES student(id)
                    ON DELETE CASCADE
            );
        """)
        self.conn.commit()
        print("[DB] Tables ready")


# single shared instance
db = Database()