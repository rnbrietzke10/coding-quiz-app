import os
import json
from os import environ
import requests
from flask import Flask, render_template, redirect, session, flash, g, jsonify
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
        return render_template('quiz.html', data=data, user=user)

    return render_template('quiz_form.html', form=form)


# Quiz Layout temp route so I don't keep calling the quizAPI

# questions = [
#     {
#         "id": 763,
#         "question": "Which of the following method of Exception class retrieve the error message when error occurred?",
#         "description": None,
#         "answers": {
#             "answer_a": "getMessage()",
#             "answer_b": "getCode()",
#             "answer_c": "getFile()",
#             "answer_d": "getLine()",
#             "answer_e": "getError()",
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": None,
#         "explanation": "getMessage() method of Exception class returns the message of exception",
#         "tip": None,
#         "tags": [
#             {
#                 "name": "PHP"
#             }
#         ],
#         "category": "Code",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 936,
#         "question": "What does HPA stand for in Kubernetes?",
#         "description": None,
#         "answers": {
#             "answer_a": "Hyper Pod Autoscaler",
#             "answer_b": "Horizontal Production Autoscaler",
#             "answer_c": "Horizontal Pod Autoscaler",
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": True,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": None,
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Kubernetes"
#             }
#         ],
#         "category": "Docker",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 127,
#         "question": "What is the correct HTML for adding a background color?",
#         "description": None,
#         "answers": {
#             "answer_a": "<body bg=\"yellow\">",
#             "answer_b": "<background>yellow</background>",
#             "answer_c": "<body style=\"background-color:yellow;\">",
#             "answer_d": "<body style bg=\"yellow\">",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": True,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_c",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "HTML"
#             }
#         ],
#         "category": "",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 551,
#         "question": "Which of the following is not a Superglobal in PHP?",
#         "description": None,
#         "answers": {
#             "answer_a": "$_SERVER",
#             "answer_b": "$_PUT",
#             "answer_c": "$_FILES",
#             "answer_d": "$_ENV",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": True,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "PHP"
#             }
#         ],
#         "category": "Code",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 301,
#         "question": "How can you call a constructor for a parent class?",
#         "description": None,
#         "answers": {
#             "answer_a": "Parents:: constructor($value)",
#             "answer_b": "Parents:: call_constructor($value)",
#             "answer_c": "Parents:: call($value)",
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "WordPress"
#             }
#         ],
#         "category": "CMS",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 1074,
#         "question": "How to change the priority of a swap file/partition to 10",
#         "description": None,
#         "answers": {
#             "answer_a": "swapon -p 10 /path/to/swapfile",
#             "answer_b": "We can't change the priority of swap partions",
#             "answer_c": "swapon -P 10 /path/to/swapfile",
#             "answer_d": "swapon +10 /path/to/swapfile",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": None,
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Linux"
#             }
#         ],
#         "category": "Linux",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 322,
#         "question": "Just installed plugin crashes your Wordpress site with no access to the dashboard. What do you do?",
#         "description": None,
#         "answers": {
#             "answer_a": "Rename the specific plugin folder in /wp-content/plugins",
#             "answer_b": "Reinstall Wordpress",
#             "answer_c": "Delete all plugins from /wp-content/plugins folder",
#             "answer_d": "Reinstall the database",
#             "answer_e": "Rename the specific plugin folder in /wp-includes/plugins",
#             "answer_f": "Rename the specific plugin folder in /wp-admin/plugins"
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "WordPress"
#             }
#         ],
#         "category": "CMS",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 739,
#         "question": "How to dump pod logs (stdout) in Kubernetes?",
#         "description": None,
#         "answers": {
#             "answer_a": "kubectl log my-pod",
#             "answer_b": "kubectl pod logs my-pod",
#             "answer_c": "kubectl logs my-pod",
#             "answer_d": "kubectl pods logs my-pod",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": True,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Kubernetes"
#             }
#         ],
#         "category": "Linux",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 824,
#         "question": "test123",
#         "description": None,
#         "answers": {
#             "answer_a": "test",
#             "answer_b": "test2",
#             "answer_c": None,
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": None,
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Angular"
#             }
#         ],
#         "category": "Linux",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 218,
#         "question": "Which SQL statement is used to return only different values?",
#         "description": None,
#         "answers": {
#             "answer_a": "DUPLICATE",
#             "answer_b": "DISTINCT",
#             "answer_c": "DIFFERENT",
#             "answer_d": "SELECT",
#             "answer_e": "None of the above",
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": True,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "MySQL"
#             }
#         ],
#         "category": "SQL",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 76,
#         "question": "The die() and exit() functions do the exact same thing.",
#         "description": None,
#         "answers": {
#             "answer_a": False,
#             "answer_b": True,
#             "answer_c": None,
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": True,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_b",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "PHP"
#             }
#         ],
#         "category": "",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 197,
#         "question": "What is the prefix of WordPress tables by default?",
#         "description": None,
#         "answers": {
#             "answer_a": "wp_ default",
#             "answer_b": "wp_",
#             "answer_c": "wp_ in",
#             "answer_d": "_wp_",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": True,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": None,
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "WordPress"
#             }
#         ],
#         "category": "CMS",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 131,
#         "question": "Which character is used to indicate an end tag?",
#         "description": None,
#         "answers": {
#             "answer_a": "/",
#             "answer_b": "<",
#             "answer_c": "*",
#             "answer_d": "^",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "HTML"
#             }
#         ],
#         "category": "",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 311,
#         "question": "What are template tags in WordPress?",
#         "description": None,
#         "answers": {
#             "answer_a": "Template tags are used within themes to retrieve content from your database.",
#             "answer_b": "Template tags are used within themes to retrieve content from your folder.",
#             "answer_c": "Template tags are used within themes to retrieve content from your plugins.",
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "WordPress"
#             }
#         ],
#         "category": "CMS",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 731,
#         "question": "How to compares the current state of the cluster against the state that the cluster would be in if the manifest was applied in Kubernetes?",
#         "description": None,
#         "answers": {
#             "answer_a": "kubectl show -f ./my-manifest.yaml",
#             "answer_b": "kubectl log -f ./my-manifest.yaml",
#             "answer_c": "kubectl state -f ./my-manifest.yaml",
#             "answer_d": "kubectl diff -f ./my-manifest.yaml",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": True,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Kubernetes"
#             }
#         ],
#         "category": "Linux",
#         "difficulty": "Easy"
#     },
#     {
#         "id": 431,
#         "question": "Which of the following is true?",
#         "description": None,
#         "answers": {
#             "answer_a": "A relation in BCNF is always in 3NF",
#             "answer_b": "BCNF and 3NF are same.",
#             "answer_c": "A relation in BCNF is not in 3NF.",
#             "answer_d": "A relation in 3NF is always in BCNF.",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "MySQL"
#             }
#         ],
#         "category": "SQL",
#         "difficulty": "Hard"
#     },
#     {
#         "id": 626,
#         "question": "What does the PHP error 'Parse error in PHP - unexpected T_variable at line x' means?",
#         "description": None,
#         "answers": {
#             "answer_a": "This is a PHP syntax error expressing that a mistake at the line x stops parsing and executing the program.",
#             "answer_b": "This is a PHP logical error expressing that a mistake at the line x stops parsing and executing the program.",
#             "answer_c": "This is a PHP warning error expressing that a mistake at the line x stops parsing and executing the program.",
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": True,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "PHP"
#             }
#         ],
#         "category": "Code",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 511,
#         "question": "Which tag is used to display the large font size?",
#         "description": None,
#         "answers": {
#             "answer_a": "<LARGE></LARGE>",
#             "answer_b": "<FONT></FONT>",
#             "answer_c": "< SIZE ></SIZE>",
#             "answer_d": "<BIG></BIG>",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": True,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "HTML"
#             }
#         ],
#         "category": "Code",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 825,
#         "question": "How to monitor Docker containers in production?",
#         "description": None,
#         "answers": {
#             "answer_a": "Docker provides functionalities like docker stats and docker events to monitor container in production.",
#             "answer_b": "Docker provides statistics like docker stats and docker events to monitor pages in production.",
#             "answer_c": "Docker provides functionalities like docker stats and docker events to monitor docker in production.",
#             "answer_d": None,
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": True,
#             "answer_d_correct": False,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_a",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "Docker"
#             }
#         ],
#         "category": "Docker",
#         "difficulty": "Medium"
#     },
#     {
#         "id": 115,
#         "question": "Which of the following is NOT a valid PHP comparison operator?",
#         "description": None,
#         "answers": {
#             "answer_a": "<=>",
#             "answer_b": ">=",
#             "answer_c": "<>",
#             "answer_d": ">==",
#             "answer_e": None,
#             "answer_f": None
#         },
#         "multiple_correct_answers": False,
#         "correct_answers": {
#             "answer_a_correct": False,
#             "answer_b_correct": False,
#             "answer_c_correct": False,
#             "answer_d_correct": True,
#             "answer_e_correct": False,
#             "answer_f_correct": False
#         },
#         "correct_answer": "answer_d",
#         "explanation": None,
#         "tip": None,
#         "tags": [
#             {
#                 "name": "PHP"
#             }
#         ],
#         "category": "",
#         "difficulty": "Medium"
#     }
# ]


# @app.route('/quiz-data')
# def get_quiz_data():
#     """
#         Pick quiz topic, number of questions, and difficulty
#     """
#
#     return jsonify(questions)


# @app.route('/quiz')
# def quiz_questions_page():
#     user = g.user
#     return render_template('quiz.html', user=user, data=questions)