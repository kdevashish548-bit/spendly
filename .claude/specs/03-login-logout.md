# Spec: Login and Logout

## Overview
This feature implements the user authentication flow, allowing users to sign into their accounts and securely sign out. It builds on the registration feature, enabling the app to identify the current user and isolate their expense data.

## Depends on
- 02-registration

## Routes
- `POST /login` — Authenticates user and starts session — public
- `GET /logout` — Terminates the user session — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/login.html` — Convert from placeholder to functional HTML form with fields for email and password.

## Files to change
- `app.py` — Implement the `POST /login` and `GET /logout` route handlers.
- `templates/login.html` — Functional login form.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] Entering correct email and password redirects user to the landing page or a protected page.
- [ ] Entering incorrect credentials shows an error message.
- [ ] Clicking logout terminates the session and redirects to the login page.
- [ ] Protected routes are inaccessible to unauthenticated users.
- [ ] Page layout remains consistent by extending `base.html`.
