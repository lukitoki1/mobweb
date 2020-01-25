import datetime
import json
from os import getenv
from uuid import uuid4

import redis

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = int(getenv('REDIS_PORT'))


class Sessions:
    exp = datetime.timedelta(minutes=5)

    def __init__(self):
        self.db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1)

    def create(self, username, password):
        session_id = str(uuid4())
        user_password_json = json.dumps({'username': username, 'password': password})
        self.db.set(session_id, user_password_json, ex=Sessions.exp)
        return session_id

    def check(self, session_id):
        if session_id is None or session_id not in self.db:
            return False
        else:
            return True

    def invalidate(self, session_id):
        self.db.delete(session_id)

    def get_credentials(self, session_id) -> (str, str):
        json_data = self.db.get(session_id)
        user_password_dict = json.loads(json_data)
        return user_password_dict['username'], user_password_dict['password']


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
