import io

import pymongo
from bson import ObjectId

from database import mongo


def allowed_files(filename: str, allowed_extensions: list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_user_by_username(username: str, projection=None):
    if projection is None:
        projection = {"_id": 0}
    return mongo.db.users.find_one({"username": username}, projection)


def get_file(file_id):
    chunk_files = list(mongo.db.fs.chunks.find({'files_id': ObjectId(file_id)}).sort([("n", pymongo.ASCENDING)]))

    with open('ontology2.owl', 'w') as file:
        for i in chunk_files:
            file.write(i['data'].decode())
