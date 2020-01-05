from os import getenv

import redis

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = int(getenv('REDIS_PORT'))


class Users:
    def __init__(self):
        self.db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.populate()

    def populate(self):
        self.db.set("test", "123")
        self.db.set('admin', 'admin')

    def check(self, login, password):
        if self.db.get(login) is None or self.db.get(login).decode("UTF-8") != password:
            return False
        return True
