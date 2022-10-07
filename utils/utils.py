import json
import os
import tempfile
from io import StringIO

import pymongo
from bson import ObjectId
from owlready2 import World

from database import mongo


def allowed_files(filename: str, allowed_extensions: list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_user_by_username(username: str, projection=None):
    if projection is None:
        projection = {"_id": 0}
    return mongo.db.users.find_one({"username": username}, projection)


def get_file(file_id):
    chunk_files = list(mongo.db.fs.chunks.find({'files_id': ObjectId(file_id)}).sort([("n", pymongo.ASCENDING)]))
    file = StringIO()
    for i in chunk_files:
        file.write(i['data'].decode())
    return file


def remove_file(file_id):
    mongo.db.fs.chunks.delete_many({'files_id': ObjectId(file_id)})
    mongo.db.fs.files.delete_one({"_id": ObjectId(file_id)})


def define_ontology(ontology_id):
    # https://owlready2.readthedocs.io/en/latest/world.html

    ontology_record = mongo.db.ontologies.find_one({"_id": ObjectId(ontology_id)})
    ontology_file = mongo.db.fs.files.find_one({"_id": ObjectId(ontology_record['file_id'])})
    ontology_chunk = get_file(ontology_record['file_id'])
    ontology_instance = World()
    with tempfile.TemporaryDirectory(dir='output') as temp_dir:
        with open(os.path.join(temp_dir, ontology_file['filename'].split('.')[0]), 'w') as file:
            file.write(ontology_chunk.getvalue())
            ontology_instance.get_ontology(file.name).load()
    return ontology_instance


def parse_json(data):
    return json.loads(json.dumps(data, default=str))
