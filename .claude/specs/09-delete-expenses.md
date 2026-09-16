# Spec: Delete Expenses

## Overview
This feature allows users to delete their expense records from the profile page. Each transaction in the Recent Transactions table will have a delete action, enabling users to remove unwanted or incorrect expense entries. This completes the CRUD operations for expense management in Spendly.

## Depends on
- Step 5: Backend routes profile page (transactions are displayed)
- Step 3: Login/Logout (session-based authentication)

## Routes
- `POST /expenses/<int:id>/delete` — Handles expense deletion — logged-in users only

## Database changes
No database changes. The `expenses` table already exists with all required fields.

## Templates
- **Modify:** `templates/profile.html` — Add delete buttons to each transaction row in the Recent Transactions table

## Files to change
- `app.py` — Implement the `POST /expenses/<int:id>/delete` route handler
- `database/queries.py` — Add `delete_expense_by_id(expense_id, user_id)` and `get_expense_by_id(expense_id, user_id)` helper functions
- `templates/profile.html` — Add delete button/icon to each transaction row
- `static/css/style.css` — Add styles for delete button and confirmation UI

## Files to create
- `tests/test_delete_expense.py` — Pytest tests for the delete expense functionality

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never string-format values into SQL
- Passwords hashed with werkzeug (not applicable to this feature)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- **Security**: Users can only delete their own expenses — verify `user_id` matches `session["user_id"]` before deletion
- **Validation**: Verify the expense exists and belongs to the logged-in user before deleting
- **User Experience**: Show a confirmation prompt before deletion (JavaScript confirm or custom modal)
- **Feedback**: Flash a success message after deletion ("Expense deleted successfully")
- **Error Handling**: If expense doesn't exist or doesn't belong to user, flash an error and redirect to profile
- After successful deletion, redirect back to `/profile` to show updated transaction list
- Delete button should be unobtrusive but accessible — consider using an icon (🗑️) or small text link

## Definition of done
- [ ] Each transaction in the Recent Transactions table has a delete button or icon
- [ ] Clicking delete shows a confirmation prompt before proceeding
- [ ] Deleting an expense removes it from the database
- [ ] After deletion, the user is redirected to `/profile` with a success message
- [ ] Summary stats (total spent, transaction count, top category) update correctly after deletion
- [ ] Category breakdown updates to reflect the deleted expense
- [ ] Users cannot delete expenses that don't belong to them (attempting to delete another user's expense returns an error)
- [ ] Attempting to delete a non-existent expense ID shows an appropriate error message
- [ ] The delete button styling is consistent with the existing Spendly design system
