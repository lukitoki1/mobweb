import requests
from flask import request, make_response, Blueprint

from .utils import create_token, wrap_response, get_username_from_token

files = Blueprint('files', __name__)


@files.route('/', methods=['GET'])
def list():
    type = request.args.get('type')
    username = get_username_from_token(request.headers.get('Authorization'))
    params = {'username': username}
    if type is not None:
        if type == 'unattached':
            params['pid'] = -1

    list_token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/files/list", headers={"Authorization": list_token}, params=params)
    return wrap_response(response)


@files.route('/<filename>', methods=['GET'])
def download(filename):
    username = get_username_from_token(request.headers.get('Authorization'))
    download_token = create_token(username, 'files', 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/files/download', params={'filename': filename, 'username': username},
                            headers={'Authorization': download_token})
    return wrap_response(response)


@files.route('/', methods=['POST'])
def upload():
    f = request.files.get('file')
    username = get_username_from_token(request.headers.get('Authorization'))
    upload_token = create_token(username, 'files', 'upload').decode('utf-8')
    response = requests.post('http://cdn:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': upload_token}, params={'username': username})
    return wrap_response(response)


@files.route('/<filename>', methods=['DELETE'])
def delete(filename):
    username = get_username_from_token(request.headers.get('Authorization'))
    delete_token = create_token(username, 'files', 'delete').decode('utf-8')
    response = requests.delete('http://cdn:5000/files/delete', headers={'Authorization': delete_token},
                               params={'filename': filename, 'username': username})
    return wrap_response(response)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
