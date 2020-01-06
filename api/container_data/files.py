import basicauth
import requests
from flask import request, make_response, Blueprint

from .utils import validate_and_decode_credentials, create_token, wrap_response

files = Blueprint('files', __name__)


@files.before_request
def check_credentials_valid():
    valid, message = validate_and_decode_credentials(request.headers.get('Authorization'))
    if not valid:
        return message
    return


@files.route('/list', methods=['GET'])
def get_files_list():
    pid = request.args.get('pid')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    params = {'username': username}
    if pid is not None:
        params['pid'] = pid

    list_token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://cdn:5000/files/list", headers={"Authorization": list_token}, params=params)
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
    response = requests.patch('http://cdn:5000/files/detach', headers={'Authorization': detach_token},
                              params={'filename': filename, 'username': username})
    return wrap_response(response)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
