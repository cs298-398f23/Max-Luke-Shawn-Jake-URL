import unittest
from flask import url_for
from app import create_app

class YourAppTests(unittest.TestCase):
    # Set up the app context
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    # Test index page loads
    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Test invalid login
    def test_invalid_login(self):
        response = self.client.post('/login', data=dict(email='nonexistent@example.com', password='wrongpassword'), follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

    # Test valid login
    def test_valid_login(self):
        response = self.client.post('/login', data=dict(email='admin@admin.com', password='admin'), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)

    # Test logout
    def test_logout(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Test login required
    def test_login_required(self):
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Test admin dashboard access
    def test_admin_dashboard_access(self):
        response = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Test view Users Page
    def test_view_users_page(self):
        response = self.client.get('/admin/view_users', follow_redirects=True)
        self.assertIn(b'Login', response.data)
    
    # Test view URLs Page
    def test_view_urls_page(self):
        response = self.client.get('/admin/view_urls', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Tear down the app context
    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()
