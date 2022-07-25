import os
from unittest import TestCase
from models import db, connect_db, User

os.environ['DATABASE_URL'] = "postgresql:///quiz_app_db_test"