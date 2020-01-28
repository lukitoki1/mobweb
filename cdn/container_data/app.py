import json
from os import getenv

import jwt
from flask import Flask
from flask import request

from .database import Notes

JWT_SECRET = getenv('JWT_SECRET')

app = Flask(__name__)
notes_db = Notes()


@app.route('/', methods=['GET'])
def get_list():
    valid, data = validate_token(request.headers.get('Authorization'), 'list')
    if not valid:
        return data

    notes_list = notes_db.list(data)
    return json.dumps(notes_list)


@app.route('/', methods=['POST'])
def upload():
    valid, data = validate_token(request.headers.get('Authorization'), 'upload')
    if not valid:
        return data

    note = json.loads(request.json)
    if not note:
        return "No note provided", 400

    notes_db.insert(note['note'], note['owner'], note['users'])
    return 'Publication uploaded', 200


def validate_token(token, proper_action):
    if token is None:
        return False, ('No token', 401)

    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        return False, ('Invalid token', 401)

    username = payload.get('username')
    if username is None:
        return False, ('Missing username', 400)

    action = payload.get('action')
    if action is None:
        return False, ('Missing action', 400)
    if action != proper_action:
        return False, (
            f'Action \"{action}\" specified in the token does not match \"{proper_action}\"', 400)

    return True, username


def decode_token(token):
    if token is None:
        return {}
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
