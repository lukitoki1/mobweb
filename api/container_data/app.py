from flask import Flask

from .files import files
from .publications import publications
from .utils import users

app = Flask(__name__)
app.register_blueprint(files, url_prefix='/files')
app.register_blueprint(publications, url_prefix='/publications')
app.register_blueprint(users, url_prefix='/users')

