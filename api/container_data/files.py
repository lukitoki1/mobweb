import requests
from flask import request, make_response, Blueprint

from .utils import create_token, wrap_response, decode_token

files = Blueprint('files', __name__)


@files.route('/', methods=['GET'])
def list():
    valid, message_or_username = decode_token(request.headers.get('Authorization'), 'files.list')
    if not valid:
        return message_or_username

    params = {'username': message_or_username}
    type = request.args.get('type')
    if type is not None:
        if type == 'unattached':
            params['pid'] = -1

    list_token = create_token(message_or_username, 'files', 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/files/list", headers={"Authorization": list_token}, params=params)
    return wrap_response(response)


@files.route('/<filename>', methods=['GET'])
def download(filename):
    valid, message_or_username = decode_token(request.headers.get('Authorization'), 'files.download')
    if not valid:
        return message_or_username

    download_token = create_token(message_or_username, 'files', 'download').decode('utf-8')
    response = requests.get('http://cdn:5000/files/download',
                            params={'filename': filename, 'username': message_or_username},
                            headers={'Authorization': download_token})
    return wrap_response(response)


@files.route('/', methods=['POST'])
def upload():
    valid, message_or_username = decode_token(request.headers.get('Authorization'), 'files.upload')
    if not valid:
        return message_or_username

    f = request.files.get('file')
    upload_token = create_token(message_or_username, 'files', 'upload').decode('utf-8')
    response = requests.post('http://cdn:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': upload_token}, params={'username': message_or_username})
    return wrap_response(response)


@files.route('/<filename>', methods=['DELETE'])
def delete(filename):
    valid, message_or_username = decode_token(request.headers.get('Authorization'), 'files.delete')
    if not valid:
        return message_or_username

    delete_token = create_token(message_or_username, 'files', 'delete').decode('utf-8')
    response = requests.delete('http://cdn:5000/files/delete', headers={'Authorization': delete_token},
                               params={'filename': filename, 'username': message_or_username})
    return wrap_response(response)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
