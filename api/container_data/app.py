from flask import Flask

from .files import files
from .publications import publications
from .users import users

app = Flask(__name__)
app.register_blueprint(files, url_prefix='/files')
app.register_blueprint(publications, url_prefix='/publications')
app.register_blueprint(users, url_prefix='/users')
