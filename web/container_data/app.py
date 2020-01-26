import json
import os
from datetime import datetime, timedelta
from os import getenv

import flask
import jwt
import requests
from flask import Flask, request, make_response, render_template, url_for
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

from .database import Sessions, Users
from .forms import LoginForm, SignupForm, ResetForm

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
SESSION_TIME = int(getenv("SESSION_TIME"))
INVALIDATE = -1

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_NAME='session_id',
    WTF_CSRF_TIME_LIMIT=None

)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

sessions_db = Sessions()
users_db = Users(bcrypt)
invalid_session_surpass_endpoints = ['login', 'logout', 'signup']


@app.before_request
def check_session_valid():
    if request.endpoint in invalid_session_surpass_endpoints:
        return
    if not sessions_db.get_username(request.cookies.get('session_id')):
        return redirect('logout')


@app.route('/', methods=['GET'])
def notes_page():
    username = sessions_db.get_username(request.cookies.get('session_id'))
    list_token = create_token(username, 'list')
    response = requests.get('http://cdn:5000/', headers={'Authorization': list_token})

    if str(response.status_code)[0] is not 2:
        return render_template('callback.html', message=response.content)

    notes = json.loads(response.content)
    return render_template('notes.html', username=username, notes=notes)


@app.route('/upload', methods=['POST'])
def upload():
    username = request.cookies.get('session_id')
    upload_token = create_token(username, 'upload')
    response = requests.post('http://cdn:5000/', headers={'Authorization': upload_token})

    if str(response.status_code)[0] is not 2:
        return render_template('callback.html', message=response.content)

    return redirect('notes_page')


@app.route('/login', methods=['GET'])
def login_page():
    login_form = LoginForm()
    return render_template('login.html', form=login_form)


@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm(request.form)

    if not login_form.validate():
        return render_template('login.html', form=login_form)

    if not users_db.check_credentials_valid(login_form.username.data, login_form.password.data):
        login_form.password.errors.append('Incorrect username or password')
        return render_template('login.html', form=login_form)

    session_id = sessions_db.create(login_form.username.data)
    response = redirect('notes_page')
    response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
    return response


@app.route('/signup', methods=['GET'])
def signup_page():
    signup_form = SignupForm()
    return flask.render_template('signup.html', form=signup_form)


@app.route('/signup', methods=['POST'])
def signup():
    signup_form = SignupForm(request.form)

    if not signup_form.validate():
        return render_template('signup.html', form=signup_form)

    if not users_db.check_username_available(signup_form.username.data):
        signup_form.username.errors.append('This username is not available')
        return render_template('signup.html', form=signup_form)

    return redirect('login_page')


@app.route('/reset', methods=['GET'])
def reset_page():
    reset_form = ResetForm()
    return render_template('reset.html', form=reset_form)


@app.route('/reset', methods=['POST'])
def reset():
    username = sessions_db.get_username(request.cookies.get('session_id'))
    reset_form = ResetForm(request.form)

    if not reset_form.validate():
        return render_template('reset.html', form=reset_form)

    if not users_db.update(username, reset_form.old_password.data, reset_form.new_password.data):
        reset_form.old_password.errors.append("Incorrect password")
        return render_template('reset.html', form=reset_form)

    return redirect('notes_page')


@app.route('/logout', methods=['GET'])
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        sessions_db.invalidate(session_id)

    response = redirect("login")
    response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
    return response


def create_token(username, action):
    exp = datetime.utcnow() + timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, 'action': action}, JWT_SECRET,
                      "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
