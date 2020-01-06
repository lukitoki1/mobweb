from flask import make_response, url_for

from .database import Sessions

sessions_db = Sessions()


def get_credentials(fwd_request):
    session_id = fwd_request.cookies.get('session_id')
    return sessions_db.get_credentials(session_id)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
