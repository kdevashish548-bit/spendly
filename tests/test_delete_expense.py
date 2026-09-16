import unittest
import os
import uuid
from app import app
import database.db as db_module
from database.db import get_db, init_db, seed_db, create_user
from database import queries
from werkzeug.security import generate_password_hash


class TestDeleteExpense(unittest.TestCase):
    def setUp(self):
        """Set up test client and temporary database."""
        self.db_file = f'test_delete_exp_{uuid.uuid4().hex[:8]}.db'
        self.original_db = db_module.DATABASE
        db_module.DATABASE = self.db_file

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()

        with app.app_context():
            init_db()
            seed_db()

    def tearDown(self):
        """Clean up after test."""
        db_module.DATABASE = self.original_db
        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
            except OSError:
                pass

    def _login_demo_user(self):
        """Helper to log in as demo user."""
        return self.client.post('/login', data={
            'email': 'demo@spendly.com',
            'password': 'demo123'
        }, follow_redirects=True)

    def test_unauthenticated_delete_redirects_to_login(self):
        """Test that unauthenticated POST to delete expense redirects to login."""
        response = self.client.post('/expenses/1/delete', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_delete_expense_success(self):
        """Test that an authenticated user can delete their own expense."""
        self._login_demo_user()

        with app.app_context():
            db = get_db()
            user = db.execute('SELECT id FROM users WHERE email = ?', ('demo@spendly.com',)).fetchone()
            user_id = user['id']

            # Check initial expense count
            initial_count = db.execute('SELECT COUNT(*) as cnt FROM expenses WHERE user_id = ?', (user_id,)).fetchone()['cnt']
            self.assertGreater(initial_count, 0)

            # Get an expense ID to delete
            expense = db.execute('SELECT id, amount, description FROM expenses WHERE user_id = ? LIMIT 1', (user_id,)).fetchone()
            expense_id = expense['id']

        # Delete the expense
        response = self.client.post(f'/expenses/{expense_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expense deleted successfully!', response.data)

        # Verify it was removed from the database
        with app.app_context():
            db = get_db()
            deleted_expense = db.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
            self.assertIsNone(deleted_expense)

            new_count = db.execute('SELECT COUNT(*) as cnt FROM expenses WHERE user_id = ?', (user_id,)).fetchone()['cnt']
            self.assertEqual(new_count, initial_count - 1)

    def test_cannot_delete_other_users_expense(self):
        """Test that a user cannot delete an expense belonging to another user."""
        unique_email = f'user2_{uuid.uuid4().hex[:8]}@example.com'
        with app.app_context():
            db = get_db()
            # Create a second user and add an expense for them
            user2_id = create_user(db, 'User Two', unique_email, generate_password_hash('pass123'))
            cursor = db.execute(
                'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
                (user2_id, 99.00, 'Food', '2026-09-15', 'Secret User2 Meal')
            )
            user2_expense_id = cursor.lastrowid
            db.commit()

        # Log in as demo user (User 1)
        self._login_demo_user()

        # Attempt to delete User 2's expense
        response = self.client.post(f'/expenses/{user2_expense_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expense not found or unauthorized.', response.data)

        # Verify User 2's expense is still in the database
        with app.app_context():
            db = get_db()
            expense = db.execute('SELECT * FROM expenses WHERE id = ?', (user2_expense_id,)).fetchone()
            self.assertIsNotNone(expense)
            self.assertEqual(expense['description'], 'Secret User2 Meal')

    def test_delete_nonexistent_expense(self):
        """Test deleting a non-existent expense ID shows an error."""
        self._login_demo_user()

        response = self.client.post('/expenses/999999/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expense not found or unauthorized.', response.data)

    def test_get_delete_route_method_not_allowed(self):
        """Test that GET request to delete route is rejected."""
        self._login_demo_user()
        response = self.client.get('/expenses/1/delete')
        self.assertEqual(response.status_code, 405)

    def test_query_helpers_delete_and_get(self):
        """Test database query helper functions directly."""
        with app.app_context():
            db = get_db()
            user = db.execute('SELECT id FROM users WHERE email = ?', ('demo@spendly.com',)).fetchone()
            user_id = user['id']

            # Insert an expense for testing helpers
            cursor = db.execute(
                'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
                (user_id, 42.50, 'Food', '2026-09-10', 'Helper Test Item')
            )
            exp_id = cursor.lastrowid
            db.commit()

            # Test get_expense_by_id
            item = queries.get_expense_by_id(exp_id, user_id, db=db)
            self.assertIsNotNone(item)
            self.assertEqual(item['amount'], 42.50)
            self.assertEqual(item['description'], 'Helper Test Item')

            # Test get_expense_by_id with wrong user
            item_wrong_user = queries.get_expense_by_id(exp_id, 99999, db=db)
            self.assertIsNone(item_wrong_user)

            # Test delete_expense_by_id
            success = queries.delete_expense_by_id(exp_id, user_id, db=db)
            self.assertTrue(success)

            # Deleting again should return False
            success_again = queries.delete_expense_by_id(exp_id, user_id, db=db)
            self.assertFalse(success_again)


if __name__ == '__main__':
    unittest.main()
