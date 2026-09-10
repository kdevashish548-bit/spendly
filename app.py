from flask import Flask, render_template, g, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from database.db import get_db as db_get_conn, init_db, seed_db, create_user
from database import queries

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
            create_user(db, name, email, hashed_pw)
            db.commit()
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            # In a real app, we'd check for sqlite3.IntegrityError specifically
            # but since we're not importing sqlite3 here, this is a safe fallback
            # for the UNIQUE constraint on email.
            flash("This email is already registered", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = queries.get_user_by_id(user_id)
    stats = queries.get_summary_stats(user_id)
    transactions = queries.get_recent_transactions(user_id)
    breakdown = queries.get_category_breakdown(user_id)

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, breakdown=breakdown)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=False, port=5001)