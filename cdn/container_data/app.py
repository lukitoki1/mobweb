import jwt
from flask import Flask, request, make_response, send_file
from dotenv import load_dotenv
from os import getenv
import json

import cdn_database

load_dotenv(verbose=True)
JWT_SECRET = getenv('JWT_SECRET')
REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = int(getenv('REDIS_PORT'))

app = Flask(__name__)

files = cdn_database.Files(REDIS_HOST, REDIS_PORT)


@app.route('/', methods=['GET'])
def list():
    token = request.headers.get('Authentication')
    valid, message = validate_and_parse_token(token, 'list')
    if not valid:
        return message

    username, action = message
    files_list = files.list(username)
    if files_list is None or len(files_list) == 0:
        return json.dumps([])
    return json.dumps(files_list)


@app.route('/<filename>', methods=['GET'])
def download(filename):
    token = request.headers.get('Authentication')
    valid, message = validate_and_parse_token(token, 'download')
    if not valid:
        return message

    username, action = message
    file = files.download(username, filename)
    return send_file(file, attachment_filename=filename)


@app.route('/', methods=['POST'])
def upload():
    f = request.files.get('file')
    token = request.headers.get('Authentication')

    valid, message = validate_and_parse_token(token, 'upload')
    if not valid:
        return message

    username, action = message
    if f.filename is "":
        return 'No file provided', 400

    files.upload(username, f.filename, f.read())
    f.close()
    return 'File uploaded', 200


@app.route('/<filename>', methods=['DELETE'])
def delete(filename):
    token = request.headers.get('Authentication')
    valid, message = validate_and_parse_token(token, 'delete')
    if not valid:
        return message

    username, action = message
    files.delete(username, filename)
    return 'File deleted', 200


def validate_and_parse_token(token, action_context):
    if token is None:
        return False, ('No token', 401)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return False, ('Invalid token', 401)

    username = payload.get('username')
    if username is None:
        return False, ('Missing username', 404)

    action = payload.get('action')
    if action is None:
        return False, ('Missing action', 404)
    if action != action_context:
        return False, ('Action specified in the token does not match the action expected for the URL', 401)

    return True, (username, action)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
