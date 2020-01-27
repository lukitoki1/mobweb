from os import environ

import flask
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, jsonify, session, url_for
from requests import HTTPError
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException

from files import files
from publications import publications
from utils import redirect

AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
AUTH0_BASE_URL = 'https://' + environ.get('AUTH0_DOMAIN')
AUTH0_AUDIENCE = environ.get('AUTH0_AUDIENCE')
SECRET_KEY = environ.get('SECRET_KEY')

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


@app.errorhandler(HTTPError)
def handle_api_downtime(ex: HTTPError):
    return render_template('callback.html', communicate="Cannot connect to REST API.", endpoint=url_for('logout')), 503


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
