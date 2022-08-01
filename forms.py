from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, validators


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


class CreateQuizForm(FlaskForm):
    """Form to select quiz topic, number of questions and difficulty"""
    tags = SelectField('Quiz Topics', choices=[('docker', 'Docker'), ('devops', 'DevOps'), ('laravel', 'Laravel'),
                                                ('html', 'HTML'), ('php', 'PHP'), ('javascript', 'JavaScript'),
                                                ('wordpress', 'WordPress'), ('bash', 'Bash'),
                                                (None, 'Random Questions')])
    limit = SelectField('Number of Questions', choices=[(5, 5), (10, 10), (15, 15), (20, 20)])
    difficulty = SelectField('Question Difficulty', choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'),
                                                             (None, 'Random')])
