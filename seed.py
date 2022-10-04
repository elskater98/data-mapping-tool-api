import os

import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient


class Seed:
    def __init__(self):
        pass

    def init_all(self):
        self.init_database()
        self.create_output_dir()

    def create_output_dir(self):
        if not os.path.exists('output'):
            os.mkdir('output')

    def init_database(self):
        client = MongoClient(os.getenv('MONGO_URI'))
        db = client['data_mapping_tool']

        if not db['users'].find_one({"username": os.getenv('ADMIN_EMAL')}):
            db['users'].insert_one(
                {"username": os.getenv('ADMIN_EMAL'),
                 "password": bcrypt.hashpw(os.getenv('ADMIN_PASSWORD').encode(), bcrypt.gensalt(10)).decode(),
                 "roles": 'Admin'})


if __name__ == '__main__':
    load_dotenv()
    s = Seed()
    s.init_all()
