import io
import json
from os import getenv

import basicauth
import requests
from flask import Flask, send_file, request, make_response, render_template

from .database import Sessions

SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

app = Flask(__name__)

session = Sessions()
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

    basic_auth = basicauth.encode(username, password)
    response = requests.get("http://api:5000/users/check", headers={"Authorization": basic_auth})
    if response.status_code is not 200:
        return invalidate_session()

    session_id = session.create(username, password)
    response = redirect('/index')
    response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
    return response


@app.route('/index')
def welcome():
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.get("http://api:5000/files/list", headers={"Authorization": basic_auth})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    files_list = json.loads(response.content)

    return render_template("index.html", listOfFiles=files_list, username=username)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    result = requests.post('http://api:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                           headers={'Authorization': basic_auth})
    return render_template('callback.html', communicate=result.content.decode('utf-8'))


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)
    response = requests.get('http://api:5000/files/download', params={'filename': filename},
                            headers={'Authorization': basic_auth})
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


def get_credentials(fwd_request):
    session_id = fwd_request.cookies.get('session_id')
    return session.get_credentials(session_id)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
