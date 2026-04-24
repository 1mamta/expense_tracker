import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "expense_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        payment_mode TEXT DEFAULT 'UPI',
        date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        monthly_limit REAL NOT NULL,
        month TEXT NOT NULL,
        UNIQUE(user_id, category, month)
    )''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password_hash=?",
              (username, hash_password(password)))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def add_expense(user_id, description, amount, category, payment_mode, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO expenses 
                 (user_id, description, amount, category, payment_mode, date)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, description, amount, category, payment_mode, date))
    conn.commit()
    conn.close()

def get_expenses(user_id, month=None):
    conn = sqlite3.connect(DB_PATH)
    if month:
        query = "SELECT * FROM expenses WHERE user_id=? AND date LIKE ? ORDER BY date DESC"
        df_rows = conn.execute(query, (user_id, f"{month}%")).fetchall()
    else:
        query = "SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC"
        df_rows = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    
    import pandas as pd
    cols = ["id", "user_id", "description", "amount", "category", 
            "payment_mode", "date", "created_at"]
    return pd.DataFrame(df_rows, columns=cols) if df_rows else pd.DataFrame(columns=cols)

def set_budget(user_id, category, limit, month):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT OR REPLACE INTO budgets (user_id, category, monthly_limit, month)
                    VALUES (?, ?, ?, ?)""", (user_id, category, limit, month))
    conn.commit()
    conn.close()

def get_budgets(user_id, month):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT category, monthly_limit FROM budgets WHERE user_id=? AND month=?",
        (user_id, month)
    ).fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def delete_expense(expense_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    conn.commit()
    conn.close()