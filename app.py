import os
from flask import Flask, render_template, redirect, session, flash, g
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import SignUpForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///quiz_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)


# Check if user in session
@app.before_request
def add_user_to_g():
    """If user is in session (logged in), add current user to Flask global object."""

    if 'CURRENT_USER_ID' in session:
        g.user = User.query.get(session['CURRENT_USER_ID'])

    else:
        g.user = None


# login, logout functions
def login_user(user):
    """Save User login to session """
    session['CURRENT_USER_ID'] = user.id


def logout_user():
    """Remove User id from session """
    if 'CURRENT_USER_ID' in session:
        del session['CURRENT_USER_ID']


"""************************* Home Page Route *************************"""


@app.route('/')
def home_page():
    return render_template('home_page.html')


"""************************* User signup, login, logout Routes  *************************"""


@app.route('/signup', methods=["GET", "POST"])
def signup_route():
    """
    Sign up new user and add to database if form information is valid.
    Login user if user is created and added to the database
    Redirect user to user homepage
    """

    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = User.sign_up(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                                username=form.username.data, password=form.password.data, image_url=form.image_url.data)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter(User.email == form.email.data).first():
                flash("Email is already taken", "db-error")
            if User.query.filter(User.username == form.username.data).first():
                flash("Username is already taken", "db-error")
            return render_template('signup_page.html', form=form)
        login_user(user)
        return redirect('/')
    else:
        return render_template('signup_page.html', form=form)
