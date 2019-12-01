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
    valid, communicate = validate_args(username, token, 'list')
    if not valid:
        return communicate

    files_list = files.list(username)
    if files_list is None or len(files_list) == 0:
        return json.dumps([])
    return json.dumps(files_list)


@app.route('/files', methods=['GET'])
def download():
    username = request.args.get('username')
    token = request.args.get('token')
    filename = request.args.get('filename')
    valid, communicate = validate_args(username, token, 'download')
    if not valid:
        return communicate

    file = files.download(username, filename)
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload():
    app.logger.error(f'data: {request.args}, file: {request.data.decode("utf-8")}')
    f = request.files.get('file')
    token = request.args.get('token')
    username = request.args.get('username')

    valid, communicate = validate_args(username, token, 'upload')
    if not valid:
        return communicate
    if f.filename is "":
        return 'No file provided', 400

    files.upload(username, f.filename, f.read())
    f.close()
    return 'File uploaded', 200


def validate_args(username, token, action):
    if username is None:
        return False, ('Missing username', 404)
    if token is None:
        return False, ('No token', 401)
    if not validate_token(token):
        return False, ('Invalid token', 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('username') != username or payload.get('action') != action:
        return False, ('Incorrect token payload', 401)
    return True, ''


def validate_token(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        return False
    return True


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
