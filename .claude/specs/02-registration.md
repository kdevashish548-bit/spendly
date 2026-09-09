# Spec: Registration

## Overview
This feature implements the user registration flow, allowing new users to create an account by providing their name, email, and password. This is a foundational step in the Spendly roadmap, enabling user-specific data isolation for expense tracking.

## Depends on!
- 01-database-setup

## Routes
- `POST /register` — Handles new user registration — public

## Database changes
No database changes. The `users` table in `database/db.py` already contains the necessary fields (`name`, `email`, `password_hash`).

## Templates
- **Modify:** `templates/register.html` — Convert from a placeholder to a functional HTML form with fields for name, email, and password.

## Files to change
- `app.py` — Implement the `POST /register` route handler with validation and database insertion.

## Files to create
- No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that the email is unique before inserting.
- Use `flash` messages to provide feedback on success or failure.

## Definition of done
- [ ] Filling the registration form with valid data creates a new user in the `users` table.
- [ ] Attempting to register with an email that already exists shows an error message.
- [ ] Passwords are stored as hashes, not plain text.
- [ ] Successful registration redirects the user to the login page.
- [ ] Page layout remains consistent by extending `base.html`.
