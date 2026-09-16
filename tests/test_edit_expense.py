import unittest
import sqlite3
import os
from database.db import init_db, seed_db, get_db
from database import queries


class TestEditExpense(unittest.TestCase):
    def setUp(self):
        # Use a separate test database
        self.db_file = 'test_expense_tracker_edit.db'
        import database.db as db_module
        self.original_db = db_module.DATABASE
        db_module.DATABASE = self.db_file

        init_db()
        seed_db()

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        import database.db as db_module
        db_module.DATABASE = self.original_db

    def test_get_expense_by_id_success(self):
        """Test fetching an expense that exists and belongs to the user."""
        with get_db() as db:
            # Get the first expense from the seed data
            expense = queries.get_expense_by_id(1, 1, db=db)

        self.assertIsNotNone(expense)
        self.assertEqual(expense['id'], 1)
        self.assertEqual(expense['user_id'], 1)
        self.assertEqual(expense['amount'], 15.50)
        self.assertEqual(expense['category'], 'Food')
        self.assertEqual(expense['description'], 'Lunch at Cafe')

    def test_get_expense_by_id_not_found(self):
        """Test fetching an expense that doesn't exist."""
        with get_db() as db:
            expense = queries.get_expense_by_id(99999, 1, db=db)

        self.assertIsNone(expense)

    def test_get_expense_by_id_wrong_user(self):
        """Test that a user cannot access another user's expense."""
        with get_db() as db:
            # Create a second user
            cursor = db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                ('User 2', 'user2@test.com', 'hash')
            )
            user2_id = cursor.lastrowid

            # Try to get user 1's expense as user 2
            expense = queries.get_expense_by_id(1, user2_id, db=db)

        self.assertIsNone(expense)

    def test_update_expense_success(self):
        """Test successfully updating an expense."""
        with get_db() as db:
            # Update the first expense
            rows_affected = queries.update_expense(
                1, 1, 25.00, 'Transport', '2026-09-10', 'Taxi ride', db=db
            )
            db.commit()

        self.assertEqual(rows_affected, 1)

        # Verify the update
        with get_db() as db:
            expense = queries.get_expense_by_id(1, 1, db=db)

        self.assertEqual(expense['amount'], 25.00)
        self.assertEqual(expense['category'], 'Transport')
        self.assertEqual(expense['date'], '2026-09-10')
        self.assertEqual(expense['description'], 'Taxi ride')

    def test_update_expense_not_found(self):
        """Test updating an expense that doesn't exist."""
        with get_db() as db:
            rows_affected = queries.update_expense(
                99999, 1, 100.00, 'Other', '2026-09-10', 'Test', db=db
            )

        self.assertEqual(rows_affected, 0)

    def test_update_expense_wrong_user(self):
        """Test that a user cannot update another user's expense."""
        with get_db() as db:
            # Create a second user
            cursor = db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                ('User 2', 'user2@test.com', 'hash')
            )
            user2_id = cursor.lastrowid

            # Try to update user 1's expense as user 2
            rows_affected = queries.update_expense(
                1, user2_id, 50.00, 'Food', '2026-09-10', 'Hacked', db=db
            )

        self.assertEqual(rows_affected, 0)

        # Verify expense was not modified
        with get_db() as db:
            expense = queries.get_expense_by_id(1, 1, db=db)

        self.assertEqual(expense['amount'], 15.50)
        self.assertEqual(expense['description'], 'Lunch at Cafe')

    def test_get_recent_transactions_includes_id(self):
        """Test that get_recent_transactions now includes the expense ID."""
        with get_db() as db:
            transactions = queries.get_recent_transactions(1, db=db)

        self.assertGreater(len(transactions), 0)
        for tx in transactions:
            self.assertIn('id', tx)
            self.assertIsInstance(tx['id'], int)


if __name__ == '__main__':
    unittest.main()
