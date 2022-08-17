from datetime import datetime
import os

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to quiz_app_db"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Database User model"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, server_default=os.path.abspath("/static/assets/blank-profile"
                                                                  "-picture-973460.svg"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    quizzes_data = db.relationship('QuizData', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def sign_up(cls, first_name, last_name, email, username, password):
        """Sign up user and store data in database if valid input"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        Check username and password match database user information.
        If unable to find matching user, or if password is wrong it should return False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_authenticated = bcrypt.check_password_hash(user.password, password)
            if is_authenticated:
                return user

        return False


class QuizData(db.Model):
    """ Database model of stored quiz data """
    __tablename__ = "quizzes_data"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_category = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    correct_questions = db.Column(JSON)
    missed_questions = db.Column(JSON)
    unanswered_questions = db.Column(JSON)
    suggested_videos = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))

