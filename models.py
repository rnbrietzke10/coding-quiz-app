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
    password = db.Column(db.Text,nullable=False)
    image_url = db.Column(db.Text,default="./static/assets/blank-profile-picture-973460.svg",)