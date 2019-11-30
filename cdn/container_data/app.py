import jwt
from flask import Flask
from flask import request
from flask import make_response
from flask import send_file
from dotenv import load_dotenv
from os import getenv
import json
import os

import cdn_database

load_dotenv(verbose=True)

app = Flask(__name__)
JWT_SECRET = getenv('JWT_SECRET')

files = cdn_database.Files()


@app.route('/list/<username>', methods=['GET'])
def list(username):
    token = request.args.get('token')
    if len(username) == 0:
        return '<h1>CDN</h1> Missing username', 404
    if token is None:
        return '<h1>CDN</h1> No token', 401
    if not valid(token):
        return '<h1>CDN</h1> Invalid token', 401
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('username') != username or payload.get('action') != 'list':
        return '<h1>CDN</h1> Incorrect token payload', 401

    files_list = files.list(username)
    app.logger.error(files_list)
    if files_list is None or len(files_list) == 0:
        return json.dumps([])
    return json.dumps(files_list)


@app.route('/files', methods=['GET'])
def download():
    username = request.args.get('username')
    token = request.args.get('token')
    filename = request.args.get('filename')
    if len(username) == 0:
        return '<h1>CDN</h1> Missing username', 404
    if token is None:
        return '<h1>CDN</h1> No token', 401
    if not valid(token):
        return '<h1>CDN</h1> Invalid token', 401
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('username') != username or payload.get('action') != 'download':
        return '<h1>CDN</h1> Incorrect token payload', 401
    file = files.download(username, filename)
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/files', methods=['POST'])
def upload():
    f = request.files.get('file')
    t = request.form.get('token')
    c = request.form.get('callback')
    username = request.form.get('username')
    if f.filename is "":
        return redirect(f"{c}?error=No+file+provided") if c \
            else ('<h1>CDN</h1> No file provided', 400)
    if t is None:
        return redirect(f"{c}?error=No+token+provided") if c \
            else ('<h1>CDN</h1> No token provided', 401)
    if not valid(t):
        return redirect(f"{c}?error=Invalid+token") if c \
            else ('<h1>CDN</h1> Invalid token', 401)
    payload = jwt.decode(t, JWT_SECRET)
    if payload.get('username') != username or payload.get('action') != 'upload':
        return '<h1>CDN</h1> Incorrect token payload', 401

    # TODO zrobic zamykanie zeby czekalo na save'a
    content_type = "multipart/form-data"
    app.logger.error(f'username: {username}, filename: {f.filename}, file: {f}')
    files.upload(username, f.filename, f.read())
    f.close()

    return redirect(f"{c}?username={username}&content_type={content_type}") if c \
        else (f'<h1>CDN</h1> Uploaded {username}', 200)


def valid(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        app.logger.error(str(e))
        return False
    return True


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
