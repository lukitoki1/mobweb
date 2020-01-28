import redis
from flask_bcrypt import Bcrypt

from .config import RedisConfig


class Users:
    def __init__(self, bcrypt: Bcrypt):
        self.db = redis.StrictRedis(host=RedisConfig.REDIS_HOST, port=RedisConfig.REDIS_PORT, db=0, charset='utf-8',
                                    decode_responses=True)
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
        if self.db.get(username):
            return False
        return True
