import jwt
from flask import request, make_response, send_file, Blueprint, url_for
from os import getenv
import json

import cdn_database

files = Blueprint('files', __name__)

JWT_SECRET = getenv('JWT_SECRET')

files_db = cdn_database.Files()


@files.route('/', methods=['GET'])
def list_or_download():
    filename = request.args.get('filename')
    if filename:
        return download(filename)

    return list()


def list():
    token = request.headers.get('Authorization')
    valid, message = validate_and_parse_token(token, 'list')
    if not valid:
        return message

    username, action = message
    files_list = files_db.list(username)
    if files_list is None or len(files_list) == 0:
        return json.dumps([])
    return json.dumps(files_list)


def download(filename):
    token = request.headers.get('Authorization')
    valid, message = validate_and_parse_token(token, 'download')
    if not valid:
        return message

    username, action = message
    file = files_db.download(username, filename)
    return send_file(file, attachment_filename=filename)


@files.route('/', methods=['POST'])
def upload():
    f = request.files.get('file')
    token = request.headers.get('Authorization')

    valid, message = validate_and_parse_token(token, 'upload')
    if not valid:
        return message

    username, action = message
    if f.filename is "":
        return 'No file provided', 400

    files_db.upload(username, f.filename, f.read())
    f.close()
    return 'File uploaded', 200


@files.route('/<filename>', methods=['DELETE'])
def delete(filename):
    token = request.headers.get('Authorization')
    valid, message = validate_and_parse_token(token, 'delete')
    if not valid:
        return message

    username, action = message
    files_db.delete(username, filename)
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
        return False, (f'Action \"{action}\" specified in the token does not match the action \"{action_context}\" expected for the URL', 401)

    return True, (username, action)

def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
