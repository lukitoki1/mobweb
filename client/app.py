from jwt import encode
from uuid import uuid4
from flask import Flask, request, make_response, session
from dotenv import load_dotenv
from os import getenv
import datetime
from redis import Redis

load_dotenv(verbose=True)

HTML = """<!doctype html>
<head><meta charset="utf-8"/></head>"""

app = Flask(__name__)
SERVER = getenv("SERVER_HOST")
CLIENT = getenv("CLIENT_HOST")
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

# redis
REDIS = getenv("REDIS_HOST")
users_db = Redis(host=REDIS, port=6379, db=0)
users_db.set('admin', 'password')

#sessions
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
app.config['SESSION_TYPE'] = "redis"
app.config['SESSION_REDIS'] = Redis(host=REDIS, port=6379, db=1)


@app.before_request
def check_session_valid():
    if not request.cookies.get('session_id') in session:
        redirect('/login')

@app.route('/')
def index():
    return redirect('/welcome')


@app.route('/login')
def login():
    return f"""{HTML}
  <h1>APP</h1>
  <form action="/auth" method="POST">
    <input type="text"     name="username" placeholder="Username"></input>
    <input type="password" name="password" placeholder="Password"></input>
    <input type="submit"/>
  </form>"""


@app.route('/welcome')
def welcome():
    session_id = request.cookies.get('session_id')
    app.logger.info(f"session_id z welcome: {session_id}")
    if session_id:
        if session_id in session:
            username = session[session_id]
        # else:
        #     fid, content_type = '', 'text/plain'
        #
        # download_token = create_download_token(fid).decode('ascii')
        upload_token = create_upload_token().decode('ascii')
        return f"""{HTML}
    <h1>APP</h1>
    
    <form action="{SERVER}/upload" method="POST" enctype="multipart/form-data">
      <input type="file" name="file"/>
      <input type="hidden" name="token"    value="{upload_token}" />
      <input type="hidden" name="callback" value="{CLIENT}/callback" />
      <input type="submit"/>
    </form> """
    return redirect("/login")


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    response = make_response('', 303)

    db_password = users_db.get(username).decode("utf-8")
    if db_password is not None and db_password == password:
        uuid = uuid4()
        session_id = str(uuid)
        session[session_id] = username
        app.logger.error(f"session_id z auth: {session_id}, uuid: {uuid}")
        response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
        response.headers["Location"] = "/welcome"
    else:
        app.logger.error(f"Nie rozpoznano {db_password} dla {username}. Powinno być {password}.")
        response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
        response.headers["Location"] = "/login"

    return response


@app.route('/logout')
def logout():
    response = redirect("/login")
    response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
    session_id = request.cookies.get('session_id')
    session.pop(session_id)
    return response


@app.route('/callback')
def uploaded():
    session_id = request.cookies.get('session_id')
    app.logger.error(f"session_id z callback: {session_id}")
    fid = request.args.get('fid')
    err = request.args.get('error')
    if err:
        return f"<h1>APP</h1> Upload failed: {err}", 400
    if not fid:
        return f"<h1>APP</h1> Upload successfull, but no fid returned", 500
    content_type = request.args.get('content_type', 'text/plain')
    return f"<h1>APP</h1> User {session_id} uploaded {fid} ({content_type})", 200


def create_download_token(fid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return encode({"iss": "client.company.com", "exp": exp}, JWT_SECRET, "HS256")


def create_upload_token():
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return encode({"iss": "client.company.com", "exp": exp}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
