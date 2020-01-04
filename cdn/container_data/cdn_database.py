import io
import os

import pymongo

MONGO_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOSTNAME = os.getenv('MONGO_HOSTNAME')


class Files:
    def __init__(self):
        self.db = pymongo.MongoClient(f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}').db
        self.files = self.db.files

    def upload(self, username, filename, file):
        self.files.insert_one({'username': username, 'filename': filename, 'file': file})

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
