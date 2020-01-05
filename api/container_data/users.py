import basicauth
from flask import Blueprint, request

from .database import Users

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
