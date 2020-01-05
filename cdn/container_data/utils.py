from os import getenv

import jwt

JWT_SECRET = getenv('JWT_SECRET')


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
        return False, (
            f'Action \"{action}\" specified in the token does not match the action \"{action_context}\" expected for '
            f'the URL', 401)

    return True, username
