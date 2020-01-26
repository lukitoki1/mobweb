import datetime
from os import getenv
from uuid import uuid4

import redis
from flask_bcrypt import Bcrypt

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = int(getenv('REDIS_PORT'))


class Sessions:
    exp = datetime.timedelta(minutes=5)

    def __init__(self):
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1, charset='utf-8', decode_responses=True)

    def create(self, username):
        session_id = str(uuid4())
        self.db.set(session_id, username, ex=Sessions.exp)
        return session_id

    def invalidate(self, session_id):
        self.db.delete(session_id)

    def get_username(self, session_id) -> str:
        return self.db.get(session_id)


class Users:
    def __init__(self, bcrypt: Bcrypt):
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
        self.bcrypt = bcrypt

    def insert(self, username, password):
        self.db.set(username, self.bcrypt.generate_password_hash(password))

    def update(self, username, old_password, new_password):
        if not self.check_credentials_valid(username, old_password):
            return False
        self.insert(username, new_password)
        return True

    def check_credentials_valid(self, username, password):
        password_hash = self.db.get(username)
        if not self.db.get(username) or not self.bcrypt.check_password_hash(password_hash, password):
            return False
        return True

    def check_username_available(self, username):
        if not self.db.get(username):
            return False
        return True
