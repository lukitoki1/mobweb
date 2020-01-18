from os import getenv, environ

import flask
from authlib.flask.client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, make_response, render_template, url_for, jsonify, session
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException

from .files import files
from .publications import publications

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = environ.get('AUTH0_AUDIENCE')
SECRET_KEY = environ.get('SECRET_KEY')
SESSION_TIME = int(getenv("SESSION_TIME"))
INVALIDATE = -1

app = Flask(__name__)
app.register_blueprint(files, url_prefix='/files')
app.register_blueprint(publications, url_prefix='/publications')
app.secret_key = SECRET_KEY
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login')
def login():
    app.logger.error('login')
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/callback')
def callback():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    print(userinfo)
    app.logger.error(userinfo)
    session['payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('files.welcome')


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': 'https://web.company.com/', 'client_id': AUTH0_CLIENT_ID}
    return flask.redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
