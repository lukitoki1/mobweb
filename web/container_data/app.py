from os import getenv

import requests
from flask import Flask, request, make_response, render_template, url_for

from .database import Sessions
from .notes import notes

SESSION_TIME = int(getenv("SESSION_TIME"))
INVALIDATE = -1

app = Flask(__name__)
app.register_blueprint(notes, url_prefix='/publications')

session = Sessions()
invalid_session_surpass_endpoints = ['login', 'auth', 'logout']


@app.before_request
def check_session_valid():
    if request.endpoint in invalid_session_surpass_endpoints:
        return
    session_id = request.cookies.get('session_id')
    if not session.check(session_id):
        return redirect('logout')


@app.route('/')
def index():
    return redirect("files.welcome")


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is "" or password is "":
        return redirect('.login')

    basic_auth = basicauth.encode(username, password)
    response = requests.get("http://api:5000/users/check", headers={"Authorization": basic_auth})
    if response.status_code is not 200:
        return redirect('app.logout')

    session_id = session.create(username, password)
    response = redirect('files.welcome')
    response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
    return response


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        session.invalidate(session_id)
    return invalidate_session()


def invalidate_session():
    response = redirect(".login")
    response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
    return response


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
