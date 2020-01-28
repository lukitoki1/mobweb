import json
import os
from datetime import datetime, timedelta
from os import getenv

import flask
import jwt
import redis
import requests
from flask import Flask, request, make_response, render_template, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.exceptions import HTTPException

from .database import Users, REDIS_HOST, REDIS_PORT
from .forms import LoginForm, SignupForm, ResetForm, NoteForm

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
SESSION_TIME = int(getenv("SESSION_TIME"))
INVALIDATE = -1

app = Flask(__name__)
app.static_folder = 'static'

app.config.update(
    SECRET_KEY=os.urandom(24),
    WTF_CSRF_TIME_LIMIT=None,
    SESSION_TYPE='redis',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_PERMANENT=False,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=5),
    SESSION_USE_SIGNER=True,
    SESSION_REDIS=redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1, charset='utf-8', decode_responses=True)
)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

users_db = Users(bcrypt)
invalid_session_surpass_endpoints = ['login_page', 'login', 'signup_page', 'signup', 'logout', 'static']


@app.errorhandler(CSRFError)
def handle_csrf_error(ex):
    return render_template('message.html', message='CSRF protection blocked your request.'), 400


@app.errorhandler(Exception)
def handle_error(ex):
    return (render_template('message.html',
                            message=f'An error occurred ({ex.code if isinstance(ex, HTTPException) else 500}).'),
            ex.code if isinstance(ex, HTTPException) else 500)


@app.before_request
def check_session_valid():
    if request.endpoint in invalid_session_surpass_endpoints:
        return
    if not session.get('username'):
        return redirect('logout')


@app.route('/', methods=['GET'])
def notes_page():
    note_form = NoteForm()
    username = session.get('username')
    status, message = fetch_notes(username)
    if not status:
        return render_template('message.html', message=message)

    return render_template('notes.html', form=note_form, username=username, notes=message)


@app.route('/', methods=['POST'])
def upload():
    username = session.get('username')
    note_form = NoteForm()
    app.logger.error(request.form)
    if not note_form.validate_on_submit():
        status, message = fetch_notes(username)
        if not status:
            return render_template('message.html', message=message)
        return render_template('notes.html', form=note_form, username=username, notes=message)

    note_dict = note_to_dict(username, note_form)
    for user in note_dict['users']:
        if users_db.check_username_available(user):
            note_form.users.errors.append('User ' + user + ' does not exist')
            status, message = fetch_notes(username)
            if not status:
                return render_template('message.html', message=message)
            return render_template('notes.html', form=note_form, username=username, notes=message)

    upload_token = create_token(username, 'upload')
    response = requests.post('http://cdn:5000/', headers={'Authorization': upload_token}, json=json.dumps(note_dict))
    if str(response.status_code)[0] != '2':
        return render_template('message.html', message=response.content)

    flash('Note added successfully')
    return redirect('notes_page')


@app.route('/login', methods=['GET'])
def login_page():
    if session.get('username'):
        return redirect('notes_page')
    login_form = LoginForm()
    return render_template('login.html', form=login_form)


@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm()
    invalid_data_laconic_message = 'Invalid username or password'

    if not login_form.validate_on_submit():
        flash(invalid_data_laconic_message, 'danger')
        return redirect('login_page')

    if not users_db.check_credentials_valid(login_form.username.data, login_form.password.data):
        flash(invalid_data_laconic_message, 'danger')
        return redirect('login_page')

    session['username'] = login_form.username.data
    return redirect('notes_page')


@app.route('/signup', methods=['GET'])
def signup_page():
    if session.get('username'):
        return redirect('notes_page')
    signup_form = SignupForm()
    return flask.render_template('signup.html', form=signup_form)


@app.route('/signup', methods=['POST'])
def signup():
    signup_form = SignupForm()

    if not signup_form.validate_on_submit():
        return render_template('signup.html', form=signup_form)

    if not users_db.check_username_available(signup_form.username.data):
        signup_form.username.errors.append('This username is not available')
        return render_template('signup.html', form=signup_form)

    users_db.insert(signup_form.username.data, signup_form.password.data)
    flash('Signed up successfully', 'success')
    return redirect('login_page')


@app.route('/reset', methods=['GET'])
def reset_page():
    reset_form = ResetForm()
    username = session.get('username')
    return render_template('reset.html', form=reset_form, username=username)


@app.route('/reset', methods=['POST'])
def reset():
    username = session.get('username')
    reset_form = ResetForm()

    if not reset_form.validate_on_submit():
        return render_template('reset.html', form=reset_form, username=username)

    if not users_db.update(username, reset_form.old_password.data, reset_form.new_password.data):
        reset_form.old_password.errors.append("Incorrect password")
        return render_template('reset.html', form=reset_form, username=username)

    flash('Changed password successfully')
    return redirect('notes_page')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("login_page")

def note_to_dict(username, note_form: NoteForm):
    note_note = note_form.note.data
    note_users = set(map(lambda x: x.strip(), note_form.users.data.split(',')))
    if '' in note_users:
        note_users.remove('')
    if username in note_users:
        note_users.remove(username)
    return {'note': note_note, 'owner': username, 'users': list(note_users)}


def fetch_notes(username):
    list_token = create_token(username, 'list')
    response = requests.get('http://cdn:5000/', headers={'Authorization': list_token})
    if str(response.status_code)[0] != '2':
        return False, response.content
    return True, json.loads(response.content)


def create_token(username, action):
    exp = datetime.utcnow() + timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, 'action': action}, JWT_SECRET,
                      "HS256")


def redirect(location, content=''):
    response = make_response(content, 303)
    response.headers["Location"] = url_for(location)
    return response
