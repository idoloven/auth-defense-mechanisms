import sqlite3
import os
from contextlib import contextmanager

DB_FILE = '../assets/users.db'

class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.init_db()
        
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        create = not os.path.exists(DB_FILE)
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT,
                totp_secret TEXT,
                category TEXT,
                failed_attempts INTEGER DEFAULT 0,
                lockout_until REAL
            )
        ''')
            
            conn.commit()
        if create:
            print(f"Database created: {DB_FILE}")
        else:
            print(f"Database initialized: {DB_FILE}")
            
                  
    def register_user(self, user):
        with self._connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (username, password, salt, totp_secret, category) VALUES (?, ?, ?, ?, ?)",
                    (user.username, user.password, user.salt, user.totp_secret, user.category)
                )
                conn.commit()
            except sqlite3.IntegrityError: # sqlite will check username uniqueness
                raise ValueError("Username already exists")
      
            
    def get_user(self, username: str):
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM clients WHERE username = ?",
                (username,)
            )
            user = cur.fetchone()
            # todo create user instance..
            return user
        
        
    def update_failed_attempts(self, user):
        with self._connect() as conn:
            if user.lockout_time:
                conn.execute(
                    "UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE username = ?",
                    (user.attempts, user.lockout_time, user.username)
                )
            else:
                conn.execute(
                    "UPDATE users SET failed_attempts = ? WHERE username = ?",
                    (user.attempts, user.username)
                )
            conn.commit()
