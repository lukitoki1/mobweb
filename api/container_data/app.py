import datetime
import io
import json
from os import getenv

import jwt
import requests
from flask import Flask, send_file, request, make_response, render_template

from .database import Users

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")

app = Flask(__name__)

users = Users()


@app.before_request
def check_session_valid():
    pass


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
        response = redirect('/index')
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
    upload_token = create_token(username, 'files', 'upload').decode('utf-8')
    result = requests.post('http://cdn:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                           headers={'Authorization': upload_token}, params={'username': username})
    return render_template('callback.html', communicate=result.content.decode('utf-8'))


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    username = get_username(request)
    download_token = create_token(username, 'files', 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/files/download', params={'filename': filename, 'username': username},
                            headers={'Authorization': download_token})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    return send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    return invalidate_session()


def invalidate_session():
    response = redirect("/login")
    return response


def get_username(fwd_request):
    session_id = fwd_request.cookies.get('session_id')


def get_files_list(username):
    list_token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/files/list", headers={"Authorization": list_token},
                            params={'username': username})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    return json.loads(response.content)


def create_token(username, datatype, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": datatype + '.' + action},
                      JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
