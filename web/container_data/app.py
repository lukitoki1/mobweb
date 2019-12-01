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

app = Flask(__name__)
CDN = getenv("CDN_HOST")
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

users = web_database.Users()
session = web_database.Sessions()

invalid_session_surpass_endpoints = ['login', 'auth']


@app.before_request
def check_session_valid():
    if request.endpoint in invalid_session_surpass_endpoints:
        return
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return redirect('/login')
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
    if f.filename == '':
        return
    username = get_username(request)
    upload_token = create_token(username, 'upload').decode('utf-8')
    result = requests.post('http://cdn:5000/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                           params={'username': username, 'token': upload_token})
    return render_template('callback.html', communicate=result.content.decode('utf-8'))


@app.route('/callback')
def callback():
    username = request.args.get('username')
    err = request.args.get('error')

    if err:
        communicate = f'Upload failed: {err}'
    else:
        content_type = request.args.get('content_type')
        filename = request.args.get('filename')
        communicate = f'User {username} uploaded {filename} ({content_type})'

    return render_template('callback.html', communicate=communicate)


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    if filename == '':
        return
    username = get_username(request)
    download_token = create_token(username, 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/download', params={'username': username, 'token': download_token, 'filename': filename})
    app.logger.error(response)
    app.logger.error(response.content)
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
    return json.loads(requests.get("http://cdn:5000/list", params={'username': username, 'token': list_token}).content)


def create_token(username, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": action}, JWT_SECRET,
                      "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
