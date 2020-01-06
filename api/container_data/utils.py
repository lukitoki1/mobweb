import datetime
from os import getenv

import basicauth
import jwt
from flask import Blueprint, request, Response

from .database import Users

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")

users = Blueprint('users', __name__)

users_db = Users()


@users.route('/check', methods=['GET'])
def check_user():
    result, message = validate_and_decode_credentials(request.headers.get('Authorization'))
    if not result:
        return message
    return '', 200


def validate_and_decode_credentials(credentials):
    if credentials is None:
        return False, ('No credentials', 401)

    username, password = basicauth.decode(credentials)

    if len(username) == 0 or len(password) == 0:
        return False, ('Incomplete credentials', 404)

    if not users_db.check(username, password):
        return False, ('Wrong username or password', 404)

    return True, username


def create_token(username, datatype, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": datatype + '.' + action},
                      JWT_SECRET, "HS256")


def wrap_response(fwd_response: Response):
    return fwd_response.content, fwd_response.status_code, fwd_response.headers.items()
