import json

from flask import request, send_file, Blueprint

from .utils import validate_and_decode_token, files_db

files = Blueprint('files', __name__)


@files.before_request
def check_token_valid():
    valid, message = validate_and_decode_token(request.headers.get('Authorization'), request.endpoint)
    if not valid:
        return message
    return


@files.route('/list', methods=['GET'])
def list():
    username = request.args.get('username')
    pid = request.args.get('pid')

    files_list = files_db.list(username, pid)
    if files_list is None or len(files_list) == 0:
        return json.dumps([]), 200
    return json.dumps(files_list), 200


@files.route('/download', methods=['GET'])
def download():
    username = request.args.get('username')
    filename = request.args.get('filename')
    if filename is None:
        return 'No filename provided', 400

    file = files_db.download(username, filename)
    return send_file(file, attachment_filename=filename)


@files.route('/upload', methods=['POST'])
def upload():
    username = request.args.get('username')

    f = request.files.get('file')
    if f.filename is "":
        return 'No file provided', 400

    result, message = files_db.upload(username, f.filename, f.read())
    f.close()
    if not result:
        return message, 401
    return 'File uploaded', 200


@files.route('/delete', methods=['DELETE'])
def delete():
    username = request.args.get('username')
    filename = request.args.get('filename')

    files_db.delete(username, filename)
    return 'File deleted', 200


@files.route('/attach', methods=['PATCH'])
def attach():
    username = request.args.get('username')
    filename = request.args.get('filename')
    pid = request.args.get('pid')
    if pid is None:
        return 'No publication ID provided'

    files_db.attach(username, filename, pid)
    return 'File attached', 200


@files.route('/detach', methods=['PATCH'])
def detach():
    username = request.args.get('username')
    filename = request.args.get('filename')

    files_db.detach(username, filename=filename)
    return 'File detached', 200
