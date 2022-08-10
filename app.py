import os
import json
from os import environ
import requests
from flask import Flask, render_template, redirect, session, flash, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import SignUpForm, LoginForm, UpdateProfileForm, CreateQuizForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///quiz_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

API_KEY = environ.get('API_KEY')
BASE_URL = 'https://quizapi.io/api/v1/questions'


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
                                username=form.username.data, password=form.password.data)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter(User.email == form.email.data).first():
                flash("Email is already taken", "danger")
            if User.query.filter(User.username == form.username.data).first():
                flash("Username is already taken", "danger")
            return render_template('signup_page.html', form=form)
        login_user(user)
        return redirect('/')
    else:
        return render_template('signup_page.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def user_login_route():
    """
    Show login form for GET request
    POST request authenticate users credentials
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            login_user(user)
            flash(f"Welcome Back, {user.first_name}!", "success")
            return redirect(f"/users/dashboard/{user.id}")
        flash("Invalid credentials.", 'danger')
    return render_template("login_page.html", form=form)


@app.route("/logout")
def logout_route():
    """Handle user logout"""
    logout_user()
    flash("Successfully Logged out!", "info")
    return redirect('/')


@app.route('/users/profile/<int:user_id>')
def user_home_page(user_id):
    """Route user to home page of specified user if friends with user or in study group with user
    if the user is not logged in redirect to home page
    """
    user = g.user
    if user:
        return render_template("user_homepage.html", user=user)

    return redirect("/")


@app.route('/users/dashboard/<int:user_id>')
def user_dashboard(user_id):
    """Route user to dashboard if logged-in user is authenticated.
    If the user is not logged or trying to get to another user's dashboard redirect them to the home page
    """
    user = g.user
    if user:
        print("Image url: ", user.image_url)
        return render_template("user_homepage.html", user=user)

    return redirect("/")


@app.route('/quiz', methods=["GET", "POST"])
def quiz_creation_page():
    """
    Pick quiz topic, number of questions, and difficulty
    """
    user = g.user
    form = CreateQuizForm()
    if form.validate_on_submit():
        """Get random quiz questions
            res.content returns a byte string and then is converted into a python dictionary using json.loads()
            """

        params = {
            'limit': int(form.limit.data),
        }
        if form.tags.data != 'None':
            params['tags'] = form.tags.data
        if form.difficulty.data != 'None':
            params['difficulty'] = form.difficulty.data

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36',
            'X-Api-Key': API_KEY,
        }
        res = requests.get(BASE_URL, headers=headers, params=params)

        res_json = res.content
        data = json.loads(res_json)
        session['data'] = data
        return render_template('quiz.html', data=data, user=user)

    return render_template('quiz_form.html', form=form)


@app.route('/quiz-results-data', methods=["GET", "POST"])
def quiz_results():
    results = request.get_json()
    session['results'] = results

    checked_results = check_answers(results)
    return jsonify(checked_results)


{'answers': {'answer_a': 'php artisan maintenance', 'answer_b': 'php artisan down', 'answer_c': 'php artisan stop',
             'answer_d': 'php artisan pause', 'answer_e': None, 'answer_f': None}, 'category': 'Code',
 'correct_answer': 'answer_a',
 'correct_answers': {'answer_a_correct': 'false', 'answer_b_correct': 'true', 'answer_c_correct': 'false',
                     'answer_d_correct': 'false', 'answer_e_correct': 'false', 'answer_f_correct': 'false'},
 'description': None, 'difficulty': 'Easy', 'explanation': None, 'id': 1067, 'multiple_correct_answers': 'false',
 'question': 'Which artisan command will you used to enable maintenance mode in Laravel?',
 'tags': [{'name': 'Laravel'}], 'tip': None}


def check_answers(results):
    question_data = session['data']
    keysList = list(results['answers'].keys())
    # question_ids = [id for id in keysList]
    print('**************************************************************')
    print(results)
    print('**************************************************************')
    # print(keysList)
    checked_answers = {
        'missed_questions': [],
        'correct_questions': [],
        'did_not_answer': []
    }
    print('LENGTH:', len(question_data))
    print('Results Length: ', len(results['answers']))
    for question in question_data:
        user_answer = results['answers'].get(str(question['id']))
        if user_answer is not None:
            if question['correct_answer'] in user_answer:
                print('CORRECT')
                checked_answers['correct_questions'].append(question['question'])
            elif question['correct_answer'] not in user_answer:
                checked_answers['missed_questions'].append(question['question'])
                print("INCORRECT")
    len_checked_questions = len(checked_answers['missed_questions']) + len(checked_answers['correct_questions'])
    if len(question_data) != len_checked_questions:
        for question in question_data:
            if question['question'] not in checked_answers['missed_questions'] and question['question'] not in checked_answers['correct_questions']:
                checked_answers['did_not_answer'].append(question['question'])
    return checked_answers


@app.route('/quiz-results')
def quiz_results_page():
    results = session['results']
    return render_template('quiz-results.html', results=results)
