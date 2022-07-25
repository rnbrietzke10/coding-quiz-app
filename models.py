from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to quiz_app_db"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Database User model"""
    __tablename__ = "users"
    id = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    first_name =  db.Column(db.Text, nullable=False)
    last_name =  db.Column(db.Text, nullable=False)
    email =  db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="./static/assets/blank-profile-picture-973460.svg")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def sign_up(cls, first_name, last_name, email, username, password, image_url):
        """Sign up user and store data in database if valid input"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(first_name=first_name,last_name=last_name, email=email, username=username,password=hashed_pwd, image_url=image_url)

        db.session.add(user)
        return user
