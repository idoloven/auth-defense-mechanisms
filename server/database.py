import os
import sqlite3
from user import User
from contextlib import contextmanager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
DB_FILE = os.path.join(ASSETS_DIR, 'users.db')

class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.init_db()
        
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
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
                is_locked INTEGER DEFAULT 0,
                rl_window_start INTEGER DEFAULT 0,
                rl_window_attempts INTEGER DEFAULT 0,
                captcha_attempts INTEGER DEFAULT 0
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
                    "INSERT INTO users (username, password_hash, salt, totp_secret, category) VALUES (?, ?, ?, ?, ?)",
                    (user.username, user.password, user.salt, user.totp_secret, user.category)
                )
                conn.commit()
            except sqlite3.IntegrityError: # sqlite will check username uniqueness
                raise ValueError("Username already exists")
      
            
    def get_user(self, username: str):
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cur.fetchone()
            return User(row["username"],
                        row["password_hash"],
                        row["category"],
                        totp_secret = row["totp_secret"],
                        salt = row["salt"],
                        failed_attempts = row["failed_attempts"],
                        is_locked = row["is_locked"],
                        rl_window_start = row["rl_window_start"],
                        rl_window_attempts = row["rl_window_attempts"],
                        captcha_attempts = row["captcha_attempts"])
        
        
    def update_failed_attempts(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET failed_attempts = ? WHERE username = ?",
                (user.failed_attempts, user.username)
            )
            conn.commit()

    def lock_account(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET is_locked = 1 WHERE username = ?",
                (user.username,)
            )
            conn.commit()
            
    def is_locked(self, user):
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT is_locked FROM users WHERE username = ?",
                (user.username,)
            )
            is_locked = cur.fetchone()
            return bool(is_locked[0])
        
    def increase_window_attempts(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET rl_window_attempts = ? WHERE username = ?",
                (user.rl_window_attempts + 1, user.username)
            )
            conn.commit()
    
    def set_new_window(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET rl_window_attempts = 1, rl_window_start = ? WHERE username = ?",
                (user.rl_window_start, user.username)
            )
            conn.commit()
            
    def increase_captcha_attempts(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET captcha_attempts = ? WHERE username = ?",
                (user.captcha_attempts + 1, user.username)
            )
            conn.commit()
    
    def reset_captcha_attempts(self, user):
        with self._connect() as conn:   
            conn.execute(
                "UPDATE users SET captcha_attempts = 1 WHERE username = ?",
                (user.username,)
            )
            conn.commit()