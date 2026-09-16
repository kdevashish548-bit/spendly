from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id, db=None):
    """Returns user details: name, email, member_since."""
    if db is None:
        with get_db() as db:
            return _get_user_by_id(db, user_id)
    else:
        return _get_user_by_id(db, user_id)

def _get_user_by_id(db, user_id):
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

def get_summary_stats(user_id, db=None):
    """Returns total_spent, transaction_count, top_category."""
    if db is None:
        with get_db() as db:
            return _get_summary_stats(db, user_id)
    else:
        return _get_summary_stats(db, user_id)

def _get_summary_stats(db, user_id):
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

def get_recent_transactions(user_id, limit=10, db=None):
    """Returns list of recent transactions."""
    if db is None:
        with get_db() as db:
            return _get_recent_transactions(db, user_id, limit)
    else:
        return _get_recent_transactions(db, user_id, limit)

def _get_recent_transactions(db, user_id, limit):
    cursor = db.execute(
        'SELECT id, date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?',
        (user_id, limit)
    )
    return [dict(row) for row in cursor.fetchall()]

def get_monthly_expenses(user_id, db=None):
    """Returns total expenses for the current month."""
    if db is None:
        with get_db() as db:
            return _get_monthly_expenses(db, user_id)
    else:
        return _get_monthly_expenses(db, user_id)

def _get_monthly_expenses(db, user_id):
    # Get total expenses for the current month
    row = db.execute(
        '''
        SELECT SUM(amount) as monthly_total
        FROM expenses
        WHERE user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        ''',
        (user_id,)
    ).fetchone()
    return row['monthly_total'] if row['monthly_total'] is not None else 0

def get_category_breakdown(user_id, db=None):
    """Returns category totals and percentages."""
    if db is None:
        with get_db() as db:
            return _get_category_breakdown(db, user_id)
    else:
        return _get_category_breakdown(db, user_id)

def _get_category_breakdown(db, user_id):
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


# ------------------------------------------------------------------ #
# New queries for the upgraded dashboard                              #
# ------------------------------------------------------------------ #

def get_daily_spending_trend(user_id, limit=14, db=None):
    """Returns daily spending totals for the last `limit` days."""
    if db is None:
        with get_db() as db:
            return _get_daily_spending_trend(db, user_id, limit)
    else:
        return _get_daily_spending_trend(db, user_id, limit)

def _get_daily_spending_trend(db, user_id, limit):
    cursor = db.execute(
        '''
        SELECT date, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY date
        ORDER BY date DESC
        LIMIT ?
        ''',
        (user_id, limit)
    )
    rows = [{"date": row['date'], "total": row['total']} for row in cursor.fetchall()]
    rows.reverse()  # chronological order
    return rows


def get_financial_insights(user_id, db=None):
    """Returns computed financial insights for the dashboard."""
    if db is None:
        with get_db() as db:
            return _get_financial_insights(db, user_id)
    else:
        return _get_financial_insights(db, user_id)

def _get_financial_insights(db, user_id):
    # Average transaction
    avg_row = db.execute(
        'SELECT AVG(amount) as avg_amount FROM expenses WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    avg_transaction = round(avg_row['avg_amount'], 2) if avg_row['avg_amount'] else 0

    # Highest single expense
    max_row = db.execute(
        'SELECT amount, category, description, date FROM expenses WHERE user_id = ? ORDER BY amount DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    highest_expense = {
        'amount': max_row['amount'],
        'category': max_row['category'],
        'description': max_row['description'],
        'date': max_row['date'],
    } if max_row else None

    # Most frequent category (by count)
    freq_row = db.execute(
        'SELECT category, COUNT(*) as cnt FROM expenses WHERE user_id = ? GROUP BY category ORDER BY cnt DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    most_frequent_category = freq_row['category'] if freq_row else "—"

    # Number of distinct days with expenses
    days_row = db.execute(
        'SELECT COUNT(DISTINCT date) as days FROM expenses WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    active_days = days_row['days'] if days_row else 0

    # Daily average (total / active days)
    stats = get_summary_stats(user_id, db=db)
    daily_avg = round(stats['total_spent'] / active_days, 2) if active_days > 0 else 0

    return {
        'avg_transaction': avg_transaction,
        'highest_expense': highest_expense,
        'most_frequent_category': most_frequent_category,
        'active_days': active_days,
        'daily_avg': daily_avg,
    }


# ------------------------------------------------------------------ #
# Edit expense queries                                                #
# ------------------------------------------------------------------ #

def get_expense_by_id(expense_id, user_id, db=None):
    """Returns a single expense owned by the user."""
    if db is None:
        with get_db() as db:
            return _get_expense_by_id(db, expense_id, user_id)
    else:
        return _get_expense_by_id(db, expense_id, user_id)

def _get_expense_by_id(db, expense_id, user_id):
    row = db.execute(
        'SELECT id, user_id, amount, category, date, description FROM expenses WHERE id = ? AND user_id = ?',
        (expense_id, user_id)
    ).fetchone()
    if row:
        return dict(row)
    return None


def update_expense(expense_id, user_id, amount, category, date, description, db=None):
    """Updates an expense owned by the user. Returns number of rows affected."""
    if db is None:
        with get_db() as db:
            return _update_expense(db, expense_id, user_id, amount, category, date, description)
    else:
        return _update_expense(db, expense_id, user_id, amount, category, date, description)

def _update_expense(db, expense_id, user_id, amount, category, date, description):
    cursor = db.execute(
        'UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?',
        (amount, category, date, description, expense_id, user_id)
    )
    return cursor.rowcount
