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

HTML = """<!doctype html>
<head><meta charset="utf-8"/></head>"""

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
    if not session.check(session_id):
        redirect('/login')


@app.route('/')
def index():
    return redirect("/index")


# TODO block /login when user logged in.

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/index')
def welcome():
    session_id = request.cookies.get('session_id')
    if session.check(session_id):
        app.logger.error(str(session.db))
        username = session.get_username(session_id)
        download_token = create_download_token(username).decode('utf-8')
        upload_token = create_upload_token(username).decode('utf-8')
        list_token = create_list_token(username).decode('utf-8')
        files_list = json.loads(requests.get("http://cdn:5000/list/" + username + "?token=" + list_token).content)
        print(type(files_list), flush=True)
        return render_template("index.html", username=username, uploadToken=upload_token, downloadToken=download_token,
                               listToken=list_token, listOfFiles=files_list)
    else:
        response = redirect("/login")
        response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
        return response


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is not "" and password is not "":
        response = make_response('', 303)

        if users.check(username, password):
            session_id = session.create(username)
            response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
            response.headers["Location"] = "/index"
        else:
            response.set_cookie("session_id", "INVALIDATE", max_age=1)
            response.headers["Location"] = "/login"

        return response
    return redirect("/login")


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        session.invalidate(session_id)
        response = redirect("/login")
        response.set_cookie("session_id", "INVALIDATE", max_age=1)
        return response
    return redirect("/login")


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
    # session[session_id] = (username, content_type)
    return f"<h1>APP</h1> User {session_id} uploaded {username} ({content_type})", 200


def create_token(username, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": "download"}, JWT_SECRET, "HS256")


def create_download_token(username):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": "download"}, JWT_SECRET, "HS256")


def create_upload_token(username):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": "upload"}, JWT_SECRET, "HS256")


def create_list_token(username):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": "list"}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
