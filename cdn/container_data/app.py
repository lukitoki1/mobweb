import json
from os import getenv

import jwt
from flask import Flask
from flask import request

from .database import Notes

JWT_SECRET = getenv('JWT_SECRET')

app = Flask(__name__)
notes_db = Notes()


@app.before_request
def check_token_valid():
    valid, message = validate_and_decode_token(request.headers.get('Authorization'), request.endpoint)
    if not valid:
        return message
    return


@app.route('/', methods=['GET'])
def list():
    username = decode_token(request.headers.get('Authorization'))

    notes_list = notes_db.list(username)
    return json.dumps(notes_list)


@app.route('/upload', methods=['POST'])
def upload():
    note = request.form.get('note')
    if not note:
        return "No note provided", 400

    owner = request.form.get('owner')
    if not owner:
        return "No owner specified", 400

    users = list(map(lambda x: x.strip(), request.form.get('users', '').split(',')))

    notes_db.insert(note, owner, users)
    return 'Publication uploaded', 200


def validate_and_decode_token(token, action_context):
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
    if action != action_context:
        return False, (
            f'Action \"{action}\" specified in the token does not match the action \"{action_context}\" expected for '
            f'the URL', 400)

    return True, ''


def decode_token(token):
    if token is None:
        return {}
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
