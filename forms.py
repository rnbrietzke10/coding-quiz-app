from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, validators


class SignUpForm(FlaskForm):
    """User sign up form"""
    username = StringField("Username", [validators.DataRequired()])
    first_name = StringField("First Name", [validators.DataRequired()])
    last_name = StringField("Last Name", [validators.DataRequired()])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField("Password", [validators.DataRequired(validators.Length(min=8))])


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])


class UpdateProfileForm(FlaskForm):
    """Update user profile information"""
    username = StringField("Username", [validators.DataRequired()])
    first_name = StringField("First Name", [validators.DataRequired()])
    last_name = StringField("Last Name", [validators.DataRequired()])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField("Password", [validators.DataRequired(validators.Length(min=8))])
    image_url = StringField('(Optional) Image URL')