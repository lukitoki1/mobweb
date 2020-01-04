from flask import Flask, send_file
from flask import request
from flask import make_response
from flask import render_template
from dotenv import load_dotenv
from os import getenv
import datetime
import io

import web_database
import jwt
import requests
import json

load_dotenv(verbose=True)
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1
REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = int(getenv('REDIS_PORT'))

app = Flask(__name__)

users = web_database.Users(REDIS_HOST, REDIS_PORT)
session = web_database.Sessions(REDIS_HOST, REDIS_PORT)
invalid_session_surpass_endpoints = ['login', 'auth']


@app.before_request
def check_session_valid():
    if request.endpoint in invalid_session_surpass_endpoints:
        return
    session_id = request.cookies.get('session_id')
    if not session.check(session_id):
        return invalidate_session()


@app.route('/')
def index():
    return redirect("/index")


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


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


@app.route('/index')
def welcome():
    username = get_username(request)
    files_list = get_files_list(username)
    return render_template("index.html", listOfFiles=files_list, username=username)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    username = get_username(request)
    upload_token = create_token(username, 'upload').decode('utf-8')
    result = requests.post('http://cdn:5000/', files={'file': (f.filename, f.stream, f.mimetype)},
                           headers={'Authentication': upload_token})
    return render_template('callback.html', communicate=result.content.decode('utf-8'))


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    username = get_username(request)
    download_token = create_token(username, 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/', params={'filename': filename},
                            headers={'Authentication': download_token})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    return send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


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


def get_username(fwd_request):
    session_id = fwd_request.cookies.get('session_id')
    return session.get_username(session_id)


def get_files_list(username):
    list_token = create_token(username, 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/", headers={"Authentication": list_token})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    return json.loads(response.content)


def create_token(username, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": action}, JWT_SECRET,
                      "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
