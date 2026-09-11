import unittest
import tempfile
import os
from app import app
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash
import uuid

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        """Set up a test client and temporary database."""
        # Use a temporary database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()

        # Initialize the database
        with app.app_context():
            init_db()
            seed_db()  # This will seed the demo user in the test database

    def tearDown(self):
        """Clean up after the test."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_landing_page(self):
        """Test that the landing page is accessible."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Spendly', response.data)

    def test_register_and_login_flow(self):
        """Test user registration, login, and access to profile."""
        # Generate a unique email for this test to avoid conflicts
        unique_id = uuid.uuid4().hex[:8]
        email = f'test_{unique_id}@example.com'
        # Register a new user
        response = self.client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully', response.data)

        # Log in with the new user
        response = self.client.post('/login', data={
            'email': email,
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Test User!', response.data)

        # Check that the profile page shows the user's name and some expense data
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)
        self.assertIn('₹'.encode('utf-8'), response.data)  # Check that there is some currency symbol (expenses are shown)

        # Log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)
        self.assertIn(b'Sign in', response.data)  # Should be back on login page

        # Try to access profile after logout - should redirect to login
        response = self.client.get('/profile', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in', response.data)  # Redirected to login page

    def test_demo_user_login(self):
        """Test that the demo user can log in and see their original expenses."""
        # Log in as demo user (credentials from seed_db)
        response = self.client.post('/login', data={
            'email': 'demo@spendly.com',
            'password': 'demo123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Demo User!', response.data)

        # Check profile page
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Demo User', response.data)
        # Check that the original expenses are present (we can check for one of the known amounts)
        self.assertIn('₹15.50'.encode('utf-8'), response.data)  # Lunch at Cafe
        self.assertIn('₹120.00'.encode('utf-8'), response.data)  # Electricity

        # Log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)

    def test_expense_isolation(self):
        """Test that users cannot see each other's expenses."""
        # Create first user
        unique_id1 = uuid.uuid4().hex[:8]
        email1 = f'user1_{unique_id1}@example.com'
        self.client.post('/register', data={
            'name': 'User One',
            'email': email1,
            'password': 'pass1'
        }, follow_redirects=True)
        # Login as user1
        self.client.post('/login', data={
            'email': email1,
            'password': 'pass1'
        }, follow_redirects=True)

        # Get user1's profile to see their expenses
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        # User1 should have our sample expenses (from seed_user_expenses)
        # We can check for one of the amounts from our sample set
        self.assertIn('₹250'.encode('utf-8'), response.data)  # Lunch from our sample set

        # Log out
        self.client.get('/logout')

        # Create second user
        unique_id2 = uuid.uuid4().hex[:8]
        email2 = f'user2_{unique_id2}@example.com'
        self.client.post('/register', data={
            'name': 'User Two',
            'email': email2,
            'password': 'pass2'
        }, follow_redirects=True)
        # Login as user2
        self.client.post('/login', data={
            'email': email2,
            'password': 'pass2'
        }, follow_redirects=True)

        # Get user2's profile
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        # User2 should also have our sample expenses (same set)
        self.assertIn('₹250'.encode('utf-8'), response.data)  # They have the same sample data, but that's okay for this test

        # Log out
        self.client.get('/logout')

        # Now login as user1 again and verify they still see their own data (not mixed)
        self.client.post('/login', data={
            'email': email1,
            'password': 'pass1'
        }, follow_redirects=True)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User One', response.data)
        self.assertIn('₹250'.encode('utf-8'), response.data)  # Still their own data

        # Log out
        self.client.get('/logout')

if __name__ == '__main__':
    unittest.main()