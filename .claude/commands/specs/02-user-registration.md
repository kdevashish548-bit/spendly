# Spec: User Registration

## Overview
User registration allows new users to create an account by providing their name and email. This is the essential entry point for the Spendly application, enabling users to maintain their own private record of expenses.

## Depends on
01-database-setup

## Routes
- `GET /register` — Display registration form — public
- `POST /register` — Process registration form and create user — public

## Database changes
No database changes. Uses the existing `users` table created in step 01.

## Templates
- **Modify:** `templates/register.html` — Implement a form with fields for Name, Email, and Password.

## Files to change
- `app.py` — Update `/register` route to handle POST requests and implement registration logic.
- `database/db.py` — Add a `create_user(name, email, password)` helper function.

## Files to create
- None

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that the email is unique before inserting (handled by DB UNIQUE constraint, but should be caught and reported as a user-friendly error).

## Definition of done
- [ ] Accessing `/register` renders a registration form.
- [ ] Submitting the form with valid details creates a new user in the `users` table.
- [ ] Passwords in the database are stored as hashes, not plain text.
- [ ] Attempting to register with an existing email displays an error message.
- [ ] Registration redirects the user to the login page upon success.
