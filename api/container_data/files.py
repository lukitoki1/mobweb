import datetime
from os import getenv

import basicauth
import jwt
import requests
from flask import request, make_response, Blueprint
from requests import Response

from .users import validate_and_decode_credentials

JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")

files = Blueprint('files', __name__)


@files.before_request
def check_credentials_valid():
    valid, message = validate_and_decode_credentials(request.headers.get('Authorization'))
    if not valid:
        return message
    return


@files.route('/list', methods=['GET'])
def get_files_list():
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    list_token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/files/list", headers={"Authorization": list_token},
                            params={'username': username})
    return wrap_response(response)


@files.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    download_token = create_token(username, 'files', 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/files/download', params={'filename': filename, 'username': username},
                            headers={'Authorization': download_token})
    return wrap_response(response)


@files.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    upload_token = create_token(username, 'files', 'upload').decode('utf-8')
    response = requests.post('http://cdn:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': upload_token}, params={'username': username})
    return wrap_response(response)


@files.route('/delete', methods=['DELETE'])
def delete():
    filename = request.args.get('filename')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    delete_token = create_token(username, 'files', 'delete').decode('utf-8')
    response = requests.delete('http://cdn:5000/files/delete', headers={'Authorization': delete_token},
                               params={'filename': filename, 'username': username})
    return wrap_response(response)


@files.route('/attach', methods=['PATCH'])
def attach():
    filename = request.args.get('filename')
    pid = request.args.get('pid')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    attach_token = create_token(username, 'files', 'attach').decode('utf-8')
    response = requests.patch('http://cdn:5000/files/attach', headers={'Authorization': attach_token},
                              params={'filename': filename, 'pid': pid, 'username': username})
    return wrap_response(response)


@files.route('/detach', methods=['PATCH'])
def detach():
    filename = request.args.get('filename')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    detach_token = create_token(username, 'files', 'detach').decode('utf-8')
    response = requests.patch('http://cdn:5000/files/attach', headers={'Authorization': detach_token},
                              params={'filename': filename, 'username': username})
    return wrap_response(response)


def create_token(username, datatype, action):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "username": username, "action": datatype + '.' + action},
                      JWT_SECRET, "HS256")


def wrap_response(fwd_response: Response):
    return fwd_response.content, fwd_response.status_code, fwd_response.headers.items()


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
