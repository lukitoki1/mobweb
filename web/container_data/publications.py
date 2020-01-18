import json

import requests
from flask import Blueprint, request, render_template, current_app

from .utils import *

publications = Blueprint('publications', __name__)


@publications.route('/')
@requires_auth
def welcome():
    username = session['profile']['name']
    token = create_token(username, 'publications', 'list').decode('utf-8')
    publications_response = requests.get("http://api:5000/publications/list", headers={"Authorization": token})
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

    token = create_token(username, 'files', 'list').decode('utf-8')
    files_response = requests.get("http://api:5000/files/list", headers={"Authorization": token},
                                  params={'pid': '-1'})
    files_list = json.loads(files_response.content)

    return render_template("publications.html", publications=publications_list, files_list=files_list,
                           username=username)


@publications.route('/new', methods=['GET'])
@requires_auth
def new():
    username = session['profile']['name']
    return render_template('form.html', username=username)


@publications.route('/upload', methods=['POST'])
@requires_auth
def upload():
    form = request.form.to_dict()
    current_app.logger.error(form)
    username = session['profile']['name']
    token = create_token(username, 'publications', 'upload').decode('utf-8')
    response = requests.post("http://api:5000/publications/upload", data=form, headers={'Authorization': token})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('publications.welcome'))


@publications.route('/delete', methods=['GET'])
@requires_auth
def delete():
    pid = request.args.get('pid')
    username = session['profile']['name']
    token = create_token(username, 'publications', 'delete').decode('utf-8')
    response = requests.delete("http://api:5000/publications/delete", params={'pid': pid},
                               headers={"Authorization": token})
    return render_template('callback.html', communicate=response.content.decode('utf-8'),
                           endpoint=url_for('publications.welcome'))
