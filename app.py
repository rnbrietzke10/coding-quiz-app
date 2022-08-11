import os
import json
import random
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
YOUTUBE_API_KEY = environ.get('YOUTUBE_API_KEY')
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
            form_error(form)
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
    if not user:
        flash("Access unauthorized.", "danger")
        return redirect('/signup')
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


@app.route('/quiz-results-data', methods=["POST"])
def quiz_results():
    results = request.get_json()
    session['results'] = results

    checked_results = check_answers(results)
    return jsonify(checked_results)


def request_youtube_api(query):
    res = requests.get(
        f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=3&q={query}&key={YOUTUBE_API_KEY}")

    res_json = res.content
    data = json.loads(res_json)
    youtube_data = []

    for video in data['items']:
        youtube_data.append([video['snippet']['thumbnails']['default']['url'], video['id']['videoId']])

    session['youtube_data'] = youtube_data
    return youtube_data


def check_answers(results):
    question_data = session['data']

    checked_answers = {
        'num_questions': len(question_data),
        'score': 100,
        'missed_questions': [],
        'correct_questions': [],
        'did_not_answer': [],
        'suggested_videos': [['https://i.ytimg.com/vi/HCQxjQoeWpg/default.jpg', 'HCQxjQoeWpg'],
                             ['https://i.ytimg.com/vi/dxHTkqSpz-w/default.jpg', 'dxHTkqSpz-w'],
                             ['https://i.ytimg.com/vi/ozS7R0vfsEM/default.jpg', 'ozS7R0vfsEM']]
    }
    """
    video data for styling
    'suggested_videos': [['https://i.ytimg.com/vi/HCQxjQoeWpg/default.jpg', 'HCQxjQoeWpg'], ['https://i.ytimg.com/vi/dxHTkqSpz-w/default.jpg', 'dxHTkqSpz-w'], ['https://i.ytimg.com/vi/ozS7R0vfsEM/default.jpg', 'ozS7R0vfsEM']]}

    """

    for question in question_data:
        user_answer = results['answers'].get(str(question['id']))
        if user_answer is not None:
            if question['correct_answer'] in user_answer:
                checked_answers['correct_questions'].append(question['question'])
            elif question['correct_answer'] not in user_answer:
                checked_answers['missed_questions'].append(question['question'])
    len_checked_questions = len(checked_answers['missed_questions']) + len(checked_answers['correct_questions'])

    if len(question_data) != len_checked_questions:
        for question in question_data:
            if question['question'] not in checked_answers['missed_questions'] and question['question'] not in \
                    checked_answers['correct_questions']:
                checked_answers['did_not_answer'].append(question['question'])
    checked_answers['score'] = round((len(checked_answers['correct_questions']) / checked_answers['num_questions']) * 100)
    # if len(checked_answers['missed_questions']) != 0:
    #     idx = random.randint(0, len(checked_answers['missed_questions']) - 1)
    #     youtube_suggestions = request_youtube_api(checked_answers['missed_questions'][idx])
    #     checked_answers['suggested_videos'] = youtube_suggestions
    #     print(checked_answers)
    # else:
    #     if session['data']['tags'][0]['name']:
    #         youtube_suggestions = request_youtube_api(session['data']['tags'][0]['name'])
    #     elif session['data']['category']:
    #         youtube_suggestions = request_youtube_api(session['data']['category'])
    return checked_answers


@app.route('/users/dashboard/<int:user_id>/edit', methods=["GET", "POST"])
def quiz_results_page(user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user)
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/signup')
    form = UpdateProfileForm(obj=user)
    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.username = form.username.data
            user.image_url = form.image_url.data
            db.session.commit()
        except IntegrityError:
            form_error(form)
            return render_template('edit_user_info.html', form=form)

        return redirect('/')
    if user.id == g.user.id:
        return render_template('edit_user_info.html', form=form)


def form_error(form):
    db.session.rollback()
    if User.query.filter(User.email == form.email.data).first():
        flash("Email is already taken", "danger")
    if User.query.filter(User.username == form.username.data).first():
        flash("Username is already taken", "danger")



