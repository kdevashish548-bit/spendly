from flask import Flask, render_template, g, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db as db_get_conn, init_db, seed_db, create_user, seed_user_expenses
from database import queries
from functools import wraps
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-secret-key-for-spendly'

# Initialize database and seed it automatically on startup
with app.app_context():
    init_db()
    seed_db()

# ------------------------------------------------------------------ #
# Database Integration                                              #
# ------------------------------------------------------------------ #

def get_db():
    """Get a database connection from the application context."""
    if 'db' not in g:
        g.db = db_get_conn()
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ------------------------------------------------------------------ #
# Auth helpers                                                        #
# ------------------------------------------------------------------ #

def login_required(f):
    """Decorator that redirects unauthenticated users to login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to continue.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required", "error")
            return render_template("register.html")

        hashed_pw = generate_password_hash(password)
        db = get_db()
        try:
            user_id = create_user(db, name, email, hashed_pw)
            seed_user_expenses(db, user_id)
            db.commit()
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            db.rollback()
            flash("This email is already registered", "error")
            return render_template("register.html")
        except Exception as e:
            db.rollback()
            flash("An error occurred. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()           # clear any stale session data
            session["user_id"] = user['id']
            # Seed expenses for the user if they have none (idempotent)
            seed_user_expenses(db, user['id'])
            db.commit()
            return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Protected routes                                                    #
# ------------------------------------------------------------------ #

@app.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    db = get_db()

    user = queries.get_user_by_id(user_id, db=db)
    if not user:
        session.clear()
        return redirect(url_for("login"))

    stats = queries.get_summary_stats(user_id, db=db)
    monthly_expenses = queries.get_monthly_expenses(user_id, db=db)
    transactions = queries.get_recent_transactions(user_id, db=db)
    breakdown = queries.get_category_breakdown(user_id, db=db)
    daily_trend = queries.get_daily_spending_trend(user_id, db=db)
    insights = queries.get_financial_insights(user_id, db=db)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        monthly_expenses=monthly_expenses,
        transactions=transactions,
        breakdown=breakdown,
        daily_trend=daily_trend,
        insights=insights,
        now_month=datetime.now().strftime("%B %Y"),
    )


@app.route("/api/chart-data")
@login_required
def chart_data():
    """Returns JSON chart data for the logged-in user only."""
    user_id = session["user_id"]
    db = get_db()
    breakdown = queries.get_category_breakdown(user_id, db=db)
    daily_trend = queries.get_daily_spending_trend(user_id, db=db)
    return jsonify({"breakdown": breakdown, "daily_trend": daily_trend})


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
@login_required
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
@login_required
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    return "Delete expense — coming in Step 9"


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False, port=5001)
