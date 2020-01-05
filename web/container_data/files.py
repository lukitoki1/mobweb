import io
import json

import basicauth
import requests
from flask import Blueprint, render_template, request, send_file, make_response, url_for

from .database import Sessions

files = Blueprint('files', __name__)

session = Sessions()


@files.route('/')
def welcome():
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.get("http://api:5000/files/list", headers={"Authorization": basic_auth})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    files_list = json.loads(response.content)

    return render_template("files.html", listOfFiles=files_list, username=username)


@files.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.get('http://api:5000/files/download', params={'filename': filename},
                            headers={'Authorization': basic_auth})
    if response.status_code is not 200:
        return render_template('callback.html', communicate=response.content.decode('utf-8'))
    return send_file(io.BytesIO(response.content), attachment_filename=filename, as_attachment=True)


@files.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    result = requests.post('http://api:5000/files/upload', files={'file': (f.filename, f.stream, f.mimetype)},
                           headers={'Authorization': basic_auth})
    return render_template('callback.html', communicate=result.content.decode('utf-8'))


@files.route('/delete', methods=['GET'])
def delete():
    filename = request.args.get('filename')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.delete("http://api:5000/files/delete", params={'filename': filename},
                               headers={"Authorization": basic_auth})
    return render_template('callback.html', communicate=response.content.decode('utf-8'))


def get_credentials(fwd_request):
    session_id = fwd_request.cookies.get('session_id')
    return session.get_credentials(session_id)


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = url_for(location)
    return response
