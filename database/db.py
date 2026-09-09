import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'expense_tracker.db'

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def create_user(db, name, email, password_hash):
    """Inserts a new user into the database and returns the new user's ID."""
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        (name, email, password_hash)
    )
    return cursor.lastrowid


def get_user_by_email(db, email):
    """Retrieves a user from the database by their email address."""
    return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()


def init_db():
    """Creates the users and expenses tables if they don't exist."""
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.commit()

def seed_db():
    """Inserts demo data if the users table is empty."""
    with get_db() as db:
        # Check if users already exist to prevent duplication
        user_exists = db.execute('SELECT id FROM users LIMIT 1').fetchone()
        if user_exists:
            return

        # Insert Demo User
        hashed_pw = generate_password_hash('demo123')
        cursor = db.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            ('Demo User', 'demo@spendly.com', hashed_pw)
        )
        user_id = cursor.lastrowid

        # 8 Sample Expenses covering all categories
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        expenses = [
            (user_id, 15.50, 'Food', '2026-09-01', 'Lunch at Cafe'),
            (user_id, 25.00, 'Transport', '2026-09-02', 'Uber ride'),
            (user_id, 120.00, 'Bills', '2026-09-03', 'Electricity'),
            (user_id, 45.00, 'Health', '2026-09-04', 'Pharmacy'),
            (user_id, 12.99, 'Entertainment', '2026-09-05', 'Netflix'),
            (user_id, 60.00, 'Shopping', '2026-09-06', 'New Shirt'),
            (user_id, 10.00, 'Other', '2026-09-07', 'Miscellaneous'),
            (user_id, 22.00, 'Food', '2026-09-08', 'Dinner'),
        ]
        db.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            expenses
        )
        db.commit()
