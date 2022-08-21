import os
from unittest import TestCase

from models import db, User, QuizData
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///coding_quiz_test_db"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """
    Test database User model
    """

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
        """Clean up"""
        db.session.rollback()

    def test_user_model(self):
        """Test creating user"""

        user = User(first_name="test", last_name="user", email="testUser@gmail.com", username="testUser",
                    password="test_password")

        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(user.quizzes_data), 0)

    def test_user__repr__method(self):
        """
        Test to see if __repr__ returns the correct format
        """
        user = User(first_name="test", last_name="user", email="testUser@gmail.com", username="testUser",
                    password="test_password")
        db.session.add(user)
        db.session.commit()

        self.assertIn(f"<User #{user.id}: {user.username}, {user.email}>", user.__repr__())

    def test_user_sign_up_method(self):
        """
        Test if signup method works correctly
        """
        user = User.sign_up(first_name="test", last_name="user", email="testUser@gmail.com", username="testUser",
                            password="test_password")
        user_id = 250
        user.id = user_id

        self.assertIsInstance(user, User)
        user1 = User.query.get(user_id)
        self.assertIsNotNone(user1)
        self.assertEqual(user1.username, "testUser")
        self.assertEqual(user1.email, "testUser@gmail.com")
        self.assertNotEqual(user1.password, "test_password")

    def test_authentication_method(self):
        """
        Test if authentication method works correctly
        """
        authenticated_user = User.authenticate(self.test_user.username, "apples")

        self.assertIsInstance(authenticated_user, User)
        self.assertEqual(authenticated_user.id, self.test_user.id)

    def test_invalid_username_sign_up_method(self):
        """
        Test if invalid username is passed to signup that it throws an error.
        """
        user = User.sign_up(first_name="test", last_name="user", email="testUser@gmail.com", username=None,
                            password="test_password")
        user_id = 250
        user.id = user_id

        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_invalid_email_sign_up_method(self):
        """
        Test if invalid email is passed to signup that it throws an error.
        """
        user = User.sign_up(first_name="test", last_name="user", email=None, username="testUser",
                            password="test_password")
        user_id = 250
        user.id = user_id

        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_invalid_password_sign_up_method(self):
        """Test if invalid password is passed to signup that it throws an error."""
        with self.assertRaises(ValueError):
            User.sign_up(first_name="test", last_name="user", email="testUser@gmail.com", username="testUser",
                         password=None)

    def test_invalid_username_authentication(self):
        authenticated_user = User.authenticate("random_user", "apples")

        self.assertNotIsInstance(authenticated_user, User)
        self.assertFalse(authenticated_user)

    def test_invalid_password_authentication(self):
        authenticated_user = User.authenticate(self.test_user.username, "wrong_password")

        self.assertNotIsInstance(authenticated_user, User)
        self.assertFalse(authenticated_user)