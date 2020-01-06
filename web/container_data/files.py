import io
import json

import basicauth
import flask
import requests

from .utils import *

files = flask.Blueprint('files', __name__)


@files.route('/')
def welcome():
    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)

    response = requests.get("http://api:5000/files/list", headers={"Authorization": basic_auth})
    if response.status_code is not 200:
        return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                     endpoint=url_for('files'))
    files_list = json.loads(response.content)

    return flask.render_template("files.html", listOfFiles=files_list, username=username)


@files.route('/download', methods=['GET'])
def download():
    filename = flask.request.args.get('filename')
    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)

    response = requests.get('http://api:5000/files/download', params={'filename': filename},
                            headers={'Authorization': basic_auth})
    if response.status_code is not 200:
        return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                     endpoint=url_for('files.welcome'))
    return flask.send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


@files.route('/upload', methods=['POST'])
def upload():
    f = flask.request.files.get('file')
    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)

    response = requests.post('http://api:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                             headers={'Authorization': basic_auth})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('files.welcome'))


@files.route('/delete', methods=['GET'])
def delete():
    filename = flask.request.args.get('filename')
    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)

    response = requests.delete("http://api:5000/files/delete", params={'filename': filename},
                               headers={"Authorization": basic_auth})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('files.welcome'))


@files.route('/attach', methods=['POST'])
def attach():
    filename = flask.request.form.get('filename')
    pid = flask.request.form.get('pid')
    if filename == '' or pid == '' or filename is None:
        return flask.render_template('callback.html', communicate='Incomplete form data',
                                     endpoint=url_for('files.welcome'))

    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)
    response = requests.patch("http://api:5000/files/attach", params={'filename': filename, 'pid': pid},
                              headers={"Authorization": basic_auth})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('publications.welcome'))


@files.route('/detach', methods=['GET'])
def detach():
    filename = flask.request.args.get('filename')

    username, password = get_credentials(flask.request)
    basic_auth = basicauth.encode(username, password)
    response = requests.patch("http://api:5000/files/detach", params={'filename': filename},
                              headers={"Authorization": basic_auth})
    return flask.render_template('callback.html', communicate=response.content.decode('utf-8'),
                                 endpoint=url_for('publications.welcome'))
