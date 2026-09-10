from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id):
    """Returns user details: name, email, member_since."""
    with get_db() as db:
        row = db.execute('SELECT name, email, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
        if row:
            # Format created_at: "2026-09-10 10:00:00" -> "September 2026"
            try:
                dt = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                member_since = dt.strftime('%B %Y')
            except (ValueError, TypeError):
                member_since = "Unknown"

            return {
                'name': row['name'],
                'email': row['email'],
                'member_since': member_since
            }
    return None

def get_summary_stats(user_id):
    """Returns total_spent, transaction_count, top_category."""
    with get_db() as db:
        # Total spent and transaction count
        stats_row = db.execute(
            'SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # Top category
        category_row = db.execute(
            'SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1',
            (user_id,)
        ).fetchone()

        return {
            'total_spent': stats_row['total_spent'] if stats_row['total_spent'] is not None else 0,
            'transaction_count': stats_row['transaction_count'] if stats_row['transaction_count'] is not None else 0,
            'top_category': category_row['category'] if category_row else "—"
        }

def get_recent_transactions(user_id, limit=10):
    """Returns list of recent transactions."""
    with get_db() as db:
        cursor = db.execute(
            'SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?',
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_category_breakdown(user_id):
    """Returns category totals and percentages."""
    with get_db() as db:
        cursor = db.execute(
            'SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC',
            (user_id,)
        )
        rows = cursor.fetchall()

        if not rows:
            return []

        total = sum(row['amount'] for row in rows)
        if total == 0:
            return [{"name": row['name'], "amount": row['amount'], "pct": 0} for row in rows]

        breakdown = []
        current_sum = 0
        for row in rows:
            pct = round((row['amount'] / total) * 100)
            breakdown.append({
                "name": row['name'],
                "amount": row['amount'],
                "pct": pct
            })
            current_sum += pct

        # Adjust the first (largest) category to ensure total is exactly 100%
        if breakdown:
            diff = 100 - current_sum
            breakdown[0]['pct'] += diff

        return breakdown
