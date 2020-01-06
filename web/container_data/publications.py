import json

import basicauth
import requests
from flask import Blueprint, request, render_template, current_app

from .utils import *

publications = Blueprint('publications', __name__)


@publications.route('/')
def welcome():
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    publications_response = requests.get("http://api:5000/publications/list", headers={"Authorization": basic_auth})
    publications_list = json.loads(publications_response.content)

    for publication in publications_list:
        publication['authors'] = ", ".join(publication['authors'])
        files = []
        for key, value in publication['_links'].items():
            if key == 'publication':
                publication['delete'] = value['delete']
            else:
                for filename, filedata in value.items():
                    files.append({'filename': filename, 'download': filedata['download'], 'detach': filedata['detach']})

        publication['files'] = files

    files_response = requests.get("http://api:5000/files/list", headers={"Authorization": basic_auth},
                                  params={'pid': '-1'})
    files_list = json.loads(files_response.content)

    return render_template("publications.html", publications=publications_list, files_list=files_list,
                           username=username)


@publications.route('/new', methods=['GET'])
def new():
    username, password = get_credentials(request)
    return render_template('form.html', username=username)


@publications.route('/upload', methods=['POST'])
def upload():
    form = request.form.to_dict()
    current_app.logger.error(form)
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.post("http://api:5000/publications/upload", data=form, headers={'Authorization': basic_auth})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('publications.welcome'))


@publications.route('/delete', methods=['GET'])
def delete():
    pid = request.args.get('pid')
    username, password = get_credentials(request)
    basic_auth = basicauth.encode(username, password)

    response = requests.delete("http://api:5000/publications/delete", params={'pid': pid},
                               headers={"Authorization": basic_auth})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('publications.welcome'))
