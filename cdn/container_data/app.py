import jwt
import requests
from flask import Flask
from flask import request
from flask import make_response
from flask import send_file
from dotenv import load_dotenv
from os import getenv
import json

import cdn_database

load_dotenv(verbose=True)

app = Flask(__name__)
JWT_SECRET = getenv('JWT_SECRET')

files = cdn_database.Files()


@app.route('/list', methods=['GET'])
def list():
    username = request.args.get('username')
    token = request.args.get('token')
    if username is None:
        return '<h1>CDN</h1> Missing username', 404
    if token is None:
        return '<h1>CDN</h1> No token', 401
    if not valid(token):
        return '<h1>CDN</h1> Invalid token', 401
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('username') != username or payload.get('action') != 'list':
        return '<h1>CDN</h1> Incorrect token payload', 401

    files_list = files.list(username)
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


@app.route('/upload', methods=['POST'])
def upload():
    app.logger.error(f'data: {request.args}, file: {request.data.decode("utf-8")}')
    f = request.files.get('file')
    t = request.args.get('token')
    c = request.args.get('callback')
    username = request.args.get('username')
    # if f.filename is "":
    #     return redirect(f"{c}?error=No+file+provided") if c \
    #         else ('<h1>CDN</h1> No file provided', 400)
    # if t is None:
    #     return redirect(f"{c}?error=No+token+provided") if c \
    #         else ('<h1>CDN</h1> No token provided', 401)
    # if not valid(t):
    #     return redirect(f"{c}?error=Invalid+token") if c \
    #         else ('<h1>CDN</h1> Invalid token', 401)
    # payload = jwt.decode(t, JWT_SECRET)
    # if payload.get('username') != username or payload.get('action') != 'upload':
    #     return '<h1>CDN</h1> Incorrect token payload', 401

    content_type = "multipart/form-data"
    files.upload(username, f.filename, f.read())
    f.close()
    # return 'alamakota'
    return make_response('File uploaded', 200)

    # return redirect(f"{c}?username={username}&filename={f.filename}&content_type={content_type}") if c \
    #     else (f'<h1>CDN</h1> Uploaded {username}', 200)


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
