import unittest
import sqlite3
import os
from database.db import init_db, seed_db, get_db
from database import queries

class TestBackendConnection(unittest.TestCase):
    def setUp(self):
        # Use a separate test database to avoid messing with seed data
        self.db_file = 'test_expense_tracker.db'
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

    def test_get_user_by_id(self):
        # Seed user should exist
        user = queries.get_user_by_id(1)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Demo User')
        self.assertEqual(user['email'], 'demo@spendly.com')
        self.assertIn('2026', user['member_since'])

        # Non-existent user
        self.assertIsNone(queries.get_user_by_id(999))

    def test_get_summary_stats(self):
        # Seed user
        stats = queries.get_summary_stats(1)
        self.assertEqual(stats['total_spent'], 310.49)
        self.assertEqual(stats['transaction_count'], 8)
        self.assertEqual(stats['top_category'], 'Bills')

        # User with no expenses
        with get_db() as db:
            cursor = db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', ('Empty', 'empty@test.com', 'hash'))
            empty_user_id = cursor.lastrowid

        stats_empty = queries.get_summary_stats(empty_user_id)
        self.assertEqual(stats_empty['total_spent'], 0)
        self.assertEqual(stats_empty['transaction_count'], 0)
        self.assertEqual(stats_empty['top_category'], '—')

    def test_get_recent_transactions(self):
        # Seed user
        txs = queries.get_recent_transactions(1)
        self.assertEqual(len(txs), 8)
        # Check newest first (sorted by date DESC)
        self.assertEqual(txs[0]['date'], '2026-09-08')

        # User with no expenses
        with get_db() as db:
            cursor = db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', ('Empty2', 'empty2@test.com', 'hash'))
            empty_user_id = cursor.lastrowid

        self.assertEqual(queries.get_recent_transactions(empty_user_id), [])

    def test_get_category_breakdown(self):
        # Seed user
        breakdown = queries.get_category_breakdown(1)
        self.assertEqual(len(breakdown), 7)
        # Sum of pct should be 100
        self.assertEqual(sum(item['pct'] for item in breakdown), 100)
        # Highest amount should be first
        self.assertEqual(breakdown[0]['name'], 'Bills')

        # User with no expenses
        with get_db() as db:
            cursor = db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', ('Empty3', 'empty3@test.com', 'hash'))
            empty_user_id = cursor.lastrowid

        self.assertEqual(queries.get_category_breakdown(empty_user_id), [])

if __name__ == '__main__':
    unittest.main()
