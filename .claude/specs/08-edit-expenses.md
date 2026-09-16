# Spec: Edit Expenses

## Overview
This feature allows logged-in users to edit their existing expenses. Users can modify the amount, category, date, and description of any expense they previously created. This is step 08 in the Spendly roadmap and provides essential CRUD update functionality for expense management.

## Depends on
- Step 01: Database setup (tables exist)
- Step 02: Registration (users can register)
- Step 03: Login/Logout (authentication works)
- Step 05: Backend routes for profile page (queries.py exists)
- Step 07: Add expense (users can create expenses)

## Routes
- `GET /expenses/<int:id>/edit` — Renders form pre-filled with expense data — logged-in only
- `POST /expenses/<int:id>/edit` — Processes the edit form submission — logged-in only

## Database changes
No database changes. The `expenses` table already has all required columns (`id`, `user_id`, `amount`, `category`, `date`, `description`).

## Templates
- **Create:** `templates/edit_expense.html` — Form for editing an expense, pre-populated with existing values
- **Modify:** `templates/profile.html` — Add edit links/buttons next to each transaction in the recent transactions list

## Files to change
- `app.py` — Implement both GET and POST handlers for `/expenses/<int:id>/edit`
- `templates/profile.html` — Add edit links for each transaction

## Files to create
- `templates/edit_expense.html` — Edit form template
- `database/queries.py` — Add `get_expense_by_id(expense_id, user_id, db)` and `update_expense(expense_id, user_id, amount, category, date, description, db)` functions

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 only
- Parameterised queries only — never format values into SQL strings
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Authorization: users can only edit their own expenses — verify `user_id` matches `session["user_id"]` before allowing edits
- If expense not found or doesn't belong to the user, redirect to profile with an error flash message
- Validate all fields: amount must be positive, date must be valid, category and description cannot be empty
- Use `flash` messages for success/error feedback
- After successful edit, redirect to `/profile`
- The edit form should look consistent with the add expense form (if it exists)
- Display the ₹ symbol for currency throughout
- Date input should use `type="date"` for better UX
- Category should use a dropdown with predefined options: Food, Transport, Shopping, Bills, Entertainment, Health, Travelling, Other

## Definition of done
- [ ] Clicking an edit link on the profile page for an expense owned by the logged-in user loads `/expenses/<id>/edit` with a form pre-filled with that expense's data
- [ ] Submitting valid changes to the edit form updates the expense in the database
- [ ] After successful edit, user is redirected to `/profile` with a success message
- [ ] Attempting to edit an expense that doesn't exist shows an error and redirects to profile
- [ ] Attempting to edit another user's expense (by manipulating the URL) shows an error and redirects to profile
- [ ] Form validation works: amount must be positive, all required fields must be filled
- [ ] The updated expense appears with new values in the profile page's transaction list
- [ ] The edit form uses the same styling as other forms and extends `base.html`
- [ ] Currency displays with ₹ symbol
- [ ] Category dropdown contains all 8 categories
