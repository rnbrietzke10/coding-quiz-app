from app import app
from models import db, User


db.drop_all()
db.create_all()

"""
    id = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    first_name =  db.Column(db.Text, nullable=False)
    last_name =  db.Column(db.Text, nullable=False)
    email =  db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text,nullable=False)
    image_url = db.Column(db.Text,default="./static/assets/blank-profile-picture-973460.svg",)
"""


u1 = User.sign_up(
    first_name="Sharon",
    last_name="Stone",
    email="sharon@gmail.com",
    username="sharon123",
    password="apples",
    image_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cGVvcGxlfGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=800&q=60"
)

u2 = User.sign_up(
    first_name="Ryan",
    last_name="Ryan",
    email="ryan@gmail.com",
    username="ryan123",
    password="apples",
    image_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8cGVvcGxlfGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=800&q=60"
)

db.session.commit()