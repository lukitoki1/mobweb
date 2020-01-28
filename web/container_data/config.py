import os
from datetime import timedelta
from os import getenv

import redis


class JwtConfig:
    JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
    JWT_SECRET = getenv("JWT_SECRET")


class RedisConfig:
    REDIS_HOST = getenv('REDIS_HOST')
    REDIS_PORT = int(getenv('REDIS_PORT'))


class FlaskConfig:
    SECRET_KEY = os.urandom(24)
    WTF_CSRF_TIME_LIMIT = None
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(getenv("SESSION_TIME")))
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=RedisConfig.REDIS_HOST, port=RedisConfig.REDIS_PORT, db=1, charset='utf-8',
                                      decode_responses=True)
