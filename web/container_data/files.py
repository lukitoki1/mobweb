import io
import json

import flask
import requests
from flask import render_template, send_file, request

from utils import *

files = flask.Blueprint('files', __name__)


@files.route('/')
@requires_auth
def welcome():
    username = session['profile']['name']
    token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://api:5000/files/", headers={"Authorization": token})
    if response.status_code != 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'), endpoint=url_for('home'))
    files_list = json.loads(response.content)
    return render_template("files.html", listOfFiles=files_list, username=username)


@files.route('/<filename>', methods=['GET'])
@requires_auth
def download(filename):
    username = session['profile']['name']
    token = create_token(username, 'files', 'download').decode('utf-8')
    response = requests.get(f'http://api:5000/files/{filename}', headers={'Authorization': token})
    if response.status_code != 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'),
                               endpoint=url_for('files.welcome'))
    return send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


@files.route('/upload', methods=['POST'])
@requires_auth
def upload():
    f = request.files.get('file')
    username = session['profile']['name']
    token = create_token(username, 'files', 'upload').decode('utf-8')
    response = requests.post('http://api:5000/files/', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': token})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('files.welcome'))


@files.route('/delete', methods=['GET'])
@requires_auth
def delete():
    filename = request.args.get('filename')
    username = session['profile']['name']
    token = create_token(username, 'files', 'delete').decode('utf-8')
    response = requests.delete(f"http://api:5000/files/{filename}", headers={"Authorization": token})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('files.welcome'))
