import json

from flask import request, Blueprint

from .utils import files_db, publications_db
from .utils import validate_and_decode_token

publications = Blueprint('publications', __name__)


@publications.before_request
def check_token_valid():
    valid, message = validate_and_decode_token(request.headers.get('Authorization'), request.endpoint)
    if not valid:
        return message
    return


@publications.route('/list', methods=['GET'])
def list():
    username = request.args.get('username')

    publications_list = publications_db.list(username)
    if publications_list is None or len(publications_list) == 0:
        return json.dumps([])
    return json.dumps(publications_list)


@publications.route('/upload', methods=['POST'])
def upload():
    username = request.args.get('username')

    title = request.form.get('title')
    authors = request.form.get('authors').split(',')
    year = request.form.get('year')

    publications_db.upload(username, title, authors, year)
    return 'Publication uploaded', 200


@publications.route('/delete', methods=['DELETE'])
def delete():
    username = request.args.get('username')
    pid = request.args.get('pid')

    publications_db.delete(username, pid)
    files_db.detach(username, pid=pid)
    return 'Publication deleted', 200
