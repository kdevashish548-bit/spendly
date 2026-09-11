import sqlite3
from database.queries import get_user_by_id, get_summary_stats

def verify():
    conn = sqlite3.connect('expense_tracker.db')
    # Look for Demo User specifically
    user = conn.execute('SELECT id FROM users WHERE email = ?', ('demo@spendly.com',)).fetchone()
    if not user:
        print("Demo User not found in database.")
        return
    user_id = user[0]
    
    user_info = get_user_by_id(user_id)
    print(f"User Info: {user_info}")
    
    stats = get_summary_stats(user_id)
    print(f"Summary Stats: {stats}")

if __name__ == "__main__":
    verify()
