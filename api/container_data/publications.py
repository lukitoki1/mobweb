import json

import basicauth
import requests
from flask import Blueprint, request, make_response

from .utils import create_token, wrap_response

publications = Blueprint('publications', __name__)


@publications.route('/list', methods=['GET'])
def list():
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    pubications_list_token = create_token(username, 'publications', 'list').decode('utf-8')
    publications_response = requests.get("http://cdn:5000/publications/list",
                                         headers={"Authorization": pubications_list_token},
                                         params={'username': username})
    publications_list = json.loads(publications_response.content)

    for publication in publications_list:
        _links = {}
        _links['publication'] = {'delete': f"/publications/delete?pid={publication['pid']}"}
        files = _links['files'] = {}

        files_list_token = create_token(username, 'files', 'list').decode('utf-8')
        files_response = requests.get("http://cdn:5000/files/list", headers={"Authorization": files_list_token},
                                      params={'username': username, 'pid': publication['pid']})
        files_list = json.loads(files_response.content)

        for file in files_list:
            files[file] = {'download': f"/files/download?filename={file}", 'detach': f"/files/detach?filename={file}"}

        publication['_links'] = _links

    response = make_response(json.dumps(publications_list))
    response.headers['Content-Type'] = 'application/hal+json'
    return response


@publications.route('/upload', methods=['POST'])
def upload():
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    upload_token = create_token(username, 'publications', 'upload').decode('utf-8')
    response = requests.post('http://cdn:5000/publications/upload', data=request.form,
                             headers={'Authorization': upload_token}, params={'username': username})
    return wrap_response(response)


@publications.route('/delete', methods=['DELETE'])
def delete():
    pid = request.args.get('pid')
    username, _ = basicauth.decode(request.headers.get('Authorization'))
    delete_token = create_token(username, 'publications', 'delete').decode('utf-8')
    response = requests.delete('http://cdn:5000/publications/delete', headers={'Authorization': delete_token},
                               params={'pid': pid, 'username': username})
    return wrap_response(response)
