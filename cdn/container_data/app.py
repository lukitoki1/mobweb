from flask import Flask

from .notes import publications

app = Flask(__name__)
app.register_blueprint(publications, url_prefix='/publications')
