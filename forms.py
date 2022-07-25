from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, Length



class SignUpForm(FlaskForm):
    """User sign up form"""
    username = StringField("Username", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(message=("That's not a valid email address."))])
    password = PasswordField("Password", validators=[DataRequired(Length(min=8))])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    