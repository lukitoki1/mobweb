import io
from os import getenv

import redis

REDIS = getenv('REDIS_HOST')


class Files:
    def __init__(self):
        self.db = redis.Redis(host='redis', port=6379, db=2)

    def upload(self, username, filename, file):
        self.db.hset(username, filename, file)

    def list(self, username):
        user_files = self.db.hgetall(username)
        return [filename.decode('utf-8') for filename in user_files.keys()]

    def download(self, username, filename):
        binary_file = self.db.hget(username, filename)
        return io.BytesIO(binary_file)
