from flask import Flask, request

from .files import files
from .publications import publications
from .utils import validate_and_decode_token

app = Flask(__name__)
app.register_blueprint(files, url_prefix='/files')
app.register_blueprint(publications, url_prefix='/publications')


@files.before_request
def check_token_valid():
    valid, message = validate_and_decode_token(request.headers.get('Authorization'), request.endpoint)
    if not valid:
        return message
    return
