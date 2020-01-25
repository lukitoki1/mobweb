import os
from datetime import datetime

import pymongo
from pymongo.errors import DuplicateKeyError

MONGO_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOSTNAME = os.getenv('MONGO_HOSTNAME')


class Notes:
    def __init__(self):
        self.db = pymongo.MongoClient(f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}').db
        self.notes = self.db.notes

        self.notes.create_index([('note', pymongo.DESCENDING), ('owner', pymongo.ASCENDING)], unique=True)

    def insert(self, note, owner, users):
        if note is '' or note is None or owner is '' or owner is None:
            return

        try:
            self.notes.insert_one({'note': note, 'owner': owner, 'users': users, 'timestamp': datetime.utcnow()})
        except DuplicateKeyError:
            self.notes.update_one({'note': note, 'owner': owner}, {"$set": {'timestamp': datetime.utcnow()}})

    def list(self, user) -> list:
        if user is None:
            return []

        query_result = self.notes.find({'$or': [{'owner': user}, {'users': user}]}, {'_id': 0, 'timestamp': 0})
        return list(query_result)
