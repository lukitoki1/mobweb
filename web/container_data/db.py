from os import getenv

import redis
import hashlib

REDIS = getenv('REDIS_HOST')


class Users:

    def __init__(self):
        self.db = redis.Redis(host='redis', port=6379, db=0)
        self.populate_users()

    def populate_users(self):
        self.db.set("test", "123")
        self.db.set('admin', 'admin')
        self.db.set('kaminsl1', 'kaminski')

    def check_user(self, login, password):
        if self.db.get(login) is None or self.db.get(login).decode("UTF-8") != password:
            return False
        return True
