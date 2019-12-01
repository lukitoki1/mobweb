import io
import redis


class Files:
    def __init__(self, host, port):
        self.db = redis.Redis(host=host, port=port, db=2)

    def upload(self, username, filename, file):
        self.db.hset(username, filename, file)

    def list(self, username):
        user_files = self.db.hgetall(username)
        return [filename.decode('utf-8') for filename in user_files.keys()]

    def download(self, username, filename):
        binary_file = self.db.hget(username, filename)
        return io.BytesIO(binary_file)
