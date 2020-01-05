import datetime
from os import getenv
from uuid import uuid4

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


class Sessions:
    exp = datetime.timedelta(minutes=5)

    def __init__(self):
        self.db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1)

    def create(self, username):
        session_id = str(uuid4())
        self.db.set(session_id, username, ex=Sessions.exp)
        return session_id

    def check(self, session_id):
        if session_id is None or session_id not in self.db:
            return False
        else:
            return True

    def extend(self, session_id):
        username = self.get_username(session_id)
        self.db.set(session_id, username, Sessions.exp)

    def invalidate(self, session_id):
        self.db.delete(session_id)

    def get_username(self, session_id):
        username = self.db.get(session_id)
        if username is not None:
            return username.decode('utf-8')
        return None
