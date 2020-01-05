import jwt
from flask import request, make_response, send_file, Blueprint, url_for
from os import getenv
import json

import cdn_database

files = Blueprint('files', __name__)

JWT_SECRET = getenv('JWT_SECRET')

files_db = cdn_database.Files()


@files.before_request
def check_token_valid():
    valid, message = validate_and_parse_token(request.headers.get('Authorization'), request.endpoint)
    if not valid:
        return message
    return


@files.route('/list', methods=['GET'])
def list():
    username = request.args.get('username')

    files_list = files_db.list(username)
    if files_list is None or len(files_list) == 0:
        return json.dumps([])
    return json.dumps(files_list)


@files.route('/download', methods=['GET'])
def download():
    username = request.args.get('username')
    filename = request.args.get('filename')

    file = files_db.download(username, filename)
    return send_file(file, attachment_filename=filename)


@files.route('/upload', methods=['POST'])
def upload():
    username = request.args.get('username')

    f = request.files.get('file')
    if f.filename is "":
        return 'No file provided', 400

    result, message = files_db.upload(username, f.filename, f.read())
    f.close()
    if not result:
        return message
    return 'File uploaded', 200


@files.route('/delete', methods=['DELETE'])
def delete():
    username = request.args.get('username')
    filename = request.args.get('filename')

    files_db.delete(username, filename)
    return 'File deleted', 200


@files.route('/attach', methods=['PATCH'])
def attach():
    username = request.args.get('username')
    filename = request.args.get('filename')
    pid = request.args.get('pid')

    files_db.attach(username, filename, pid)
    return 'File attached', 200


@files.route('/detach', methods=['PATCH'])
def detach():
    username = request.args.get('username')
    filename = request.args.get('filename')

    files_db.detach(username, filename)
    return 'File detached', 200


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

    return True, username


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
