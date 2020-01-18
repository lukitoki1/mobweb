import io
import json

import flask
import requests

from .utils import *

files = flask.Blueprint('files', __name__)


@files.route('/')
@requires_auth
def welcome():
    username = session['profile']['name']
    token = create_token(username, 'files', 'list').decode('utf-8')
    response = requests.get("http://api:5000/files/list", headers={"Authorization": token})
    if response.status_code is not 200:
        return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                     endpoint=url_for('home'))
    files_list = json.loads(response.content)

    return flask.render_template("files.html", listOfFiles=files_list, username=username)


@files.route('/download', methods=['GET'])
@requires_auth
def download():
    filename = flask.request.args.get('filename')
    username = session['profile']['name']
    token = create_token(username, 'files', 'download').decode('utf-8')
    response = requests.get('http://api:5000/files/download', params={'filename': filename},
                            headers={'Authorization': token})
    if response.status_code is not 200:
        return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                     endpoint=url_for('files.welcome'))
    return flask.send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


@files.route('/upload', methods=['POST'])
@requires_auth
def upload():
    f = flask.request.files.get('file')
    username = session['profile']['name']
    token = create_token(username, 'files', 'upload').decode('utf-8')
    response = requests.post('http://api:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': token})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('files.welcome'))


@files.route('/delete', methods=['GET'])
@requires_auth
def delete():
    filename = flask.request.args.get('filename')
    username = session['profile']['name']
    token = create_token(username, 'files', 'delete').decode('utf-8')
    response = requests.delete("http://api:5000/files/delete", params={'filename': filename},
                               headers={"Authorization": token})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('files.welcome'))


@files.route('/attach', methods=['POST'])
@requires_auth
def attach():
    filename = flask.request.form.get('filename')
    pid = flask.request.form.get('pid')
    username = session['profile']['name']
    token = create_token(username, 'files', 'attach').decode('utf-8')
    if filename == '' or pid == '' or filename is None:
        return flask.render_template('callback.html', communicate='Incomplete form data',
                                     endpoint=url_for('files.welcome'))

    response = requests.patch("http://api:5000/files/attach", params={'filename': filename, 'pid': pid},
                              headers={"Authorization": token})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('publications.welcome'))


@files.route('/detach', methods=['GET'])
@requires_auth
def detach():
    filename = flask.request.args.get('filename')
    username = session['profile']['name']
    token = create_token(username, 'files', 'detach').decode('utf-8')
    response = requests.patch("http://api:5000/files/detach", params={'filename': filename},
                              headers={"Authorization": token})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('publications.welcome'))
