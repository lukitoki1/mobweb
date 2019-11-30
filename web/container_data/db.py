import datetime
from os import getenv
from uuid import uuid4

import redis

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


class Sessions:
    def __init__(self):
        self.db = redis.Redis(host='redis', port=6379, db=1)

    def create_session(self, login):
        session_id = str(uuid4())
        exp = datetime.datetime.now() + datetime.timedelta(minutes=5)
        exp = str(exp)
        self.db.hset('exp', session_id, exp)
        self.db.hset('username', session_id, login)
        return session_id

    def check_session(self, id):
        session = self.db.hget('username', id)
        if session is not None:
            session_exp = datetime.datetime.strptime(self.db.hget('exp', id).decode("UTF-8"),
                                                 '%Y-%m-%d %H:%M:%S.%f')
            if session_exp > datetime.datetime.now():
                return True
        return False

    def delete_session(self, id):
        self.db.hdel('exp', id)
        self.db.hdel('username', id)

    def get_username(self, id):
        return self.db.hget('username', id).decode("UTF-8")
