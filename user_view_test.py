import os
from unittest import TestCase
from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///quiz_app_db_test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create user data"""

        User.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_user_signup(self):
        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up for", html)
