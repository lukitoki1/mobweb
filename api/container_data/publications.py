import json

import requests
from flask import Blueprint, request, make_response

from .utils import create_token, wrap_response, get_username_from_token

publications = Blueprint('publications', __name__)


@publications.route('/<pid>', methods=['GET'])
@publications.route('/', methods=['GET'])
def hateoas(pid=None):
    username = get_username_from_token(request.headers.get('Authorization'))
    publications_list = get_publications(username, pid)

    for publication in publications_list:
        pid = publication['pid']
        _links = {'publication': {'delete': f"/publications/{pid}"}}
        files = _links['files'] = {}

        files_list_token = create_token(username, 'files', 'list').decode('utf-8')
        files_response = requests.get("http://cdn:5000/files/list", headers={"Authorization": files_list_token},
                                      params={'username': username, 'pid': pid})
        filenames_list = json.loads(files_response.content)

        for filename in filenames_list:
            files[filename] = {'download': f"/files/{filename}", 'detach': f"/publications/{pid}/files/{filename}"}

        publication['_links'] = _links

    response = make_response(json.dumps(publications_list))
    response.headers['Content-Type'] = 'application/hal+json'
    return response


@publications.route('/', methods=['POST'])
def upload():
    username = get_username_from_token(request.headers.get('Authorization'))
    upload_token = create_token(username, 'publications', 'upload').decode('utf-8')
    response = requests.post('http://cdn:5000/publications/upload', data=request.form,
                             headers={'Authorization': upload_token}, params={'username': username})
    return wrap_response(response)


@publications.route('/<pid>', methods=['DELETE'])
def delete(pid):
    username = get_username_from_token(request.headers.get('Authorization'))
    delete_token = create_token(username, 'publications', 'delete').decode('utf-8')
    response = requests.delete('http://cdn:5000/publications/delete', headers={'Authorization': delete_token},
                               params={'pid': pid, 'username': username})
    return wrap_response(response)


@publications.route('/<pid>/files/<filename>', methods=['POST'])
def attach(pid, filename):
    username = get_username_from_token(request.headers.get('Authorization'))
    attach_token = create_token(username, 'files', 'attach').decode('utf-8')
    response = requests.patch('http://cdn:5000/files/attach', headers={'Authorization': attach_token},
                              params={'filename': filename, 'pid': pid, 'username': username})
    return wrap_response(response)


@publications.route('/<pid>/files/<filename>', methods=['DELETE'])
def detach(pid, filename):
    username = get_username_from_token(request.headers.get('Authorization'))
    detach_token = create_token(username, 'files', 'detach').decode('utf-8')
    response = requests.patch('http://cdn:5000/files/detach', headers={'Authorization': detach_token},
                              params={'filename': filename, 'username': username})
    return wrap_response(response)


def get_publications(username, pid=None):
    params = {'username': username}
    if pid is not None and pid != '':
        params['pid'] = pid
    pubications_list_token = create_token(username, 'publications', 'list').decode('utf-8')
    publications_response = requests.get("http://cdn:5000/publications/list",
                                         headers={"Authorization": pubications_list_token},
                                         params=params)
    parsed_response = json.loads(publications_response.content)
    return parsed_response if type(parsed_response) is list else list(parsed_response)
