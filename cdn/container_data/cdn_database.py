import io
import os

import pymongo
from pymongo.errors import DuplicateKeyError

MONGO_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOSTNAME = os.getenv('MONGO_HOSTNAME')


class Files:
    def __init__(self):
        self.db = pymongo.MongoClient(f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}').db
        self.files = self.db.files
        self.files.create_index('filename', unique=True)

    def upload(self, username, filename, file):
        try:
            self.files.insert_one({'username': username, 'filename': filename, 'file': file, 'pid': None})
            return True, ''
        except DuplicateKeyError:
            return False, 'File with the exact name is already owned by the user'

    def list(self, username) -> list:
        query_result = self.files.find({'username': username}, {'_id': 0, 'filename': 1})
        query_result_list = list(query_result)

        if len(query_result_list) == 0:
            return query_result_list

        filenames_list = [filename_dict['filename'] for filename_dict in query_result_list]
        print(filenames_list)
        return filenames_list

    def download(self, username, filename):
        query_result = self.files.find_one({'username': username, 'filename': filename})
        return io.BytesIO(query_result['file'])

    def delete(self, username, filename):
        self.files.delete_one({'username': username, 'filename': filename})

    def attach(self, username, filename, pid):
        self.files.update_one({'username': username, 'filename': filename}, {"$set": {'pid': pid}})

    def detach(self, username, filename):
        self.files.update_one({'username': username, 'filename': filename}, {"$set": {'pid': None}})


class Publications:
    def __init__(self):
        self.db = pymongo.MongoClient(f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}').db
        self.publications = self.db.publications
