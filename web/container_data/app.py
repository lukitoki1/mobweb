from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from dotenv import load_dotenv
from os import getenv
import datetime

import web_database
import jwt
import requests
import json

load_dotenv(verbose=True)

app = Flask(__name__)
CDN = getenv("CDN_HOST")
WEB = getenv("WEB_HOST")
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

users = web_database.Users()
session = web_database.Sessions()


@app.before_request
def check_session_valid():
    session_id = request.cookies.get('session_id')
    if session_id is None:
        redirect('/login')
    if not session.check(session_id):
        invalidate_session()


@app.route('/')
def index():
    return redirect("/index")


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/index')
def welcome():
    session_id = request.cookies.get('session_id')
    if session.check(session_id):
        username = session.get_username(session_id)
        download_token = create_token(username, 'download').decode('utf-8')
        upload_token = create_token(username, 'upload').decode('utf-8')
        list_token = create_token(username, 'list').decode('utf-8')
        files_list = json.loads(requests.get("http://cdn:5000/list/" + username + "?token=" + list_token).content)
        return render_template("index.html", username=username, uploadToken=upload_token, downloadToken=download_token,
                               listToken=list_token, listOfFiles=files_list)
    else:
        return invalidate_session()


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is "" or password is "":
        return redirect('/login')
    if users.check(username, password):
        session_id = session.create(username)
        response = redirect('/index')
        response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
    else:
        response = invalidate_session()
    return response


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        session.invalidate(session_id)
    return invalidate_session()


def invalidate_session():
    response = redirect("/login")
    response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
    return response


@app.route('/callback')
def uploaded():
    session_id = request.cookies.get('session_id')
    username = request.args.get('username')
    err = request.args.get('error')
    if not session_id:
        return redirect("/login")

    if err:
        return f"<h1>APP</h1> Upload failed: {err}", 400
    if not username:
        return f"<h1>APP</h1> Upload successfull, but no username returned", 500
    content_type = request.args.get('content_type', 'text/plain')
    return f"<h1>APP</h1> User {session_id} uploaded {username} ({content_type})", 200


def create_token(username, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": action}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
