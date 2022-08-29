import os
import json
import random
import requests
from flask import Flask, render_template, redirect, session, flash, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, QuizData
from forms import SignUpForm, LoginForm, UpdateProfileForm, CreateQuizForm, DeleteUser

app = Flask(__name__)

uri = os.environ.get('DATABASE_URL')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

API_KEY = os.environ.get('API_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
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
    return redirect('/signup')


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
        return redirect(f"/users/dashboard/{user.id}")
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


@app.route('/users/dashboard/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user_profile(user_id):
    """
    Edit user information
    """
    user = User.query.filter_by(id=user_id).first()
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
            return render_template('edit_user_info.html', form=form, user=user)

        return redirect(f'/users/dashboard/{user_id}')
    if user.id == g.user.id:
        return render_template('edit_user_info.html', form=form, user=user)


@app.route('/users/dashboard/<int:user_id>/delete', methods=["GET", "POST"])
def delete_user(user_id):
    """Show delete user form and delete user if authenticated"""
    form = DeleteUser()
    user = User.query.filter_by(id=user_id).first()
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/signup')
    if form.validate_on_submit():
        try:
            authenticated = User.authenticate(form.username.data, form.password.data)
            if authenticated:
                logout_user()
                db.session.delete(g.user)
                db.session.commit()
                return redirect('/signup')
            else:
                flash("Error: User was unable to deleted.", "danger")
                return redirect('/login')
        except IntegrityError:
            flash("Something went wrong with deleting the user. Please login and try again", "danger")
            return redirect('/login')
    if user.id == g.user.id:
        return render_template('delete_user.html', form=form)


@app.route('/users/dashboard/<int:user_id>')
def user_dashboard(user_id):
    """Route user to dashboard if logged-in user is authenticated.
    If the user is not logged or trying to get to another user's dashboard redirect them to the home page
    """
    user = g.user
    if user.id == user_id:
        user_quiz_data = user.quizzes_data
        return render_template("user_homepage.html", user=user, user_quiz_data=user_quiz_data)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")


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
        # Store tag for database
        session["category"] = form.tags.data
        params = {
            'limit': int(form.limit.data),
        }
        if form.tags.data != 'None':
            params['tags'] = session["category"]
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

        if type(data) is dict:
            flash("No Questions found at that difficulty level. Pick a different or random difficultly level", "danger")
            return render_template('quiz_form.html', form=form)

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
        f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=3&q={session["category"]}%20{query}&key={YOUTUBE_API_KEY}')

    res_json = res.content
    data = json.loads(res_json)
    youtube_data = []
    for video in data['items']:
        youtube_data.append(
            [video['snippet']['thumbnails']['default']['url'], video['id']['videoId'], video['snippet']['title']])

    session['youtube_data'] = youtube_data

    return youtube_data


@app.route('/quiz-data/<int:quiz_id>')
def quiz_detail_page(quiz_id):
    """Show quiz details with the given id"""
    quiz_data = QuizData.query.get_or_404(quiz_id)
    video_images = []
    video_ids = []
    video_images_ids = []
    video_titles = []

    suggested_videos = quiz_data.suggested_videos.replace('{', "")
    suggested_videos = suggested_videos.replace('}', "")

    split_video_data = suggested_videos.split(',')

    for item in split_video_data:
        if 'https' in item:
            video_images.append(item)
        elif " " in item:
            first_filter = item.replace("'", "")
            second_filter = first_filter.replace('"', '')
            video_titles.append(second_filter)
        else:
            video_ids.append(item)

    video_images_ids.append((video_images[0], video_ids[0], video_titles[0]))
    video_images_ids.append((video_images[1], video_ids[1], video_titles[1]))
    video_images_ids.append((video_images[2], video_ids[2], video_titles[2]))

    return render_template('quiz_detail_page.html', quiz_data=quiz_data, video_images_ids=video_images_ids)


def check_answers(results):
    """
    Check which answers are correct and incorrect
    Store data in object and then store data in database
    """
    question_data = session['data']

    checked_answers = {
        'num_questions': len(question_data),
        'score': 100,
        'missed_questions': [],
        'correct_questions': [],
        'did_not_answer': [],
        'suggested_videos': []
    }
    youtube_suggestions = None

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
    checked_answers['score'] = round(
        (len(checked_answers['correct_questions']) / checked_answers['num_questions']) * 100)
    if len(checked_answers['missed_questions']) != 0:
        idx = random.randint(0, len(checked_answers['missed_questions']) - 1)
        youtube_suggestions = request_youtube_api(checked_answers['missed_questions'][idx])
        checked_answers['suggested_videos'] = youtube_suggestions

    else:
        idx = random.randint(0, len(session['data']) - 1)
        if session['data'][idx]['tags']['name']:
            youtube_suggestions = request_youtube_api(session['data'][idx]['tags'][0]['name'])
        elif session['data'][idx]['category']:
            youtube_suggestions = request_youtube_api(session['data'][idx]['category'])
    checked_answers['suggested_videos'] = youtube_suggestions
    store_quiz_data(checked_answers)
    return checked_answers


def form_error(form):
    """
    Check if email or username is already used and display appropriate message
    """
    db.session.rollback()
    if User.query.filter(User.email == form.email.data).first():
        flash("Email is already taken", "danger")
    if User.query.filter(User.username == form.username.data).first():
        flash("Username is already taken", "danger")


def store_quiz_data(obj):
    """Store quiz data in quizzes_data table"""
    try:
        data = QuizData(quiz_category=session["category"].title(), score=obj["score"],
                        correct_questions=obj['correct_questions'],
                        missed_questions=obj['missed_questions'], unanswered_questions=obj['did_not_answer'],
                        suggested_videos=obj['suggested_videos'], user_id=g.user.id)

        db.session.add(data)
        db.session.commit()
    except IntegrityError:
        return redirect(f'/users/dashboard/{g.user.id}')
