from flask import Flask, render_template, g, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db as db_get_conn, init_db, seed_db, create_user, get_user_by_email
from functools import wraps

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


def login_required(f):
    """Decorator to protect routes from unauthenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")

        db = get_db()
        user = get_user_by_email(db, email)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash("Welcome back!", "success")
            return redirect(url_for("landing"))

        flash("Invalid email or password", "error")
        return render_template("login.html")

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been signed out", "success")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    return "Profile page — coming in Step 4"


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


if __name__ == "__main__":
    app.run(debug=False, port=5001)