from datetime import datetime, timedelta
from os import getenv

import jwt
from flask import make_response, url_for

from .database import Sessions

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")

sessions_db = Sessions()


def create_token(username, datatype, action):
    exp = datetime.utcnow() + timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": datatype + '.' + action},
                      JWT_SECRET, "HS256")


def get_credentials(fwd_request):
    session_id = fwd_request.cookies.get('session_id')
    return sessions_db.get_credentials(session_id)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
