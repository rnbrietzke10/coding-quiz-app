import os
from unittest import TestCase
from models import db, User, QuizData

os.environ['DATABASE_URL'] = "postgresql:///coding_quiz_test_db"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """
        Create test client and sample quiz data
        """

        User.query.delete()
        QuizData.query.delete()

        self.test_user = User.sign_up(first_name="John", last_name="Doe", email="john_doe@gmail.com",
                                      username="john_doe123", password="apples")

        self.test_user.id = 1

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up """
        db.session.rollback()

    def test_user_signup(self):
        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up for", html)

    def test_user_login(self):
        with self.client as c:
            resp = c.get("/login")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", html)

    def test_user_dashboard(self):
        """
        Test user dashboard shows correct information
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess['CURRENT_USER_ID'] = self.test_user.id

            resp = c.get(f'/users/dashboard/{self.test_user.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("John", html)

