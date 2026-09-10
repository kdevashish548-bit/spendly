import sqlite3
from database.queries import get_user_by_id, get_summary_stats

def verify():
    # We need the user_id of the seed user. 
    # Let's just get the first user.
    conn = sqlite3.connect('expense_tracker.db')
    user = conn.execute('SELECT id FROM users LIMIT 1').fetchone()
    if not user:
        print("No user found in database.")
        return
    user_id = user[0]
    
    user_info = get_user_by_id(user_id)
    print(f"User Info: {user_info}")
    
    stats = get_summary_stats(user_id)
    print(f"Summary Stats: {stats}")

if __name__ == "__main__":
    verify()
