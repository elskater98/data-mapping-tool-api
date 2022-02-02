import datetime
import os.path
import uuid

import pandas as pd
import pymongo
from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.mapping import MappingModel
from utils import getUser

mapping_router = Blueprint('mapping', __name__)


@mapping_router.route("/data/sample", methods=["GET"])
@jwt_required()
def data_sample():
    identity = get_jwt_identity()
    if request.args.get('filename'):
        filename = request.args.get('filename')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], identity + '/' + filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)[:15]
            df.dropna(inplace=True)
            return jsonify(data=df.to_dict(orient="records"))
        return {"error": f"The file '{filename}' don't exist."}, 400
    return {"error": "Field 'filename' not found."}, 400


@mapping_router.route("/data/sample/columns", methods=["GET"])
@jwt_required()
def data_sample_columns():
    identity = get_jwt_identity()
    if request.args.get('filename'):
        filename = request.args.get('filename')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], identity + '/' + filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            return jsonify(columns=list(df.columns))
        return {"error": f"The file '{filename}' don't exist."}, 400
    return {"error": "Field 'filename' not found."}, 400


@mapping_router.route("/", methods=["POST"])
@jwt_required()
def create_mapping():
    identity = get_jwt_identity()
    body = request.json
    body.update({"createdBy": identity, "ref": str(uuid.uuid4()), "createdAt": datetime.datetime.utcnow()})
    mapping = MappingModel(**body)
    mongo.db.mapping.insert_one(mapping.dict())
    return jsonify(data=mapping.dict()), 201


@mapping_router.route("/", methods=["GET"])
@jwt_required()
def get_mappings():
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(
                mappings=list(mongo.db.mapping.find({}, {"_id": 0}).sort([("createdAt", pymongo.DESCENDING)])))
        else:
            return jsonify(mappings=list(mongo.db.mapping.find({"createdBy": user['username']}, {"_id": 0}).sort(
                [("createdAt", pymongo.DESCENDING)])))

    return {"error": "Unauthorized!"}, 401


@mapping_router.route("/<ref>", methods=["GET"])
@jwt_required()
def get_mapping(ref):
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(mappings=mongo.db.mapping.find_one({"ref": ref}, {"_id": 0}))
        else:
            return jsonify(mappings=mongo.db.mapping.find_one({"ref": ref, "createdBy": identity}, {"_id": 0}))
    return {"error": "Unauthorized!"}, 401


@mapping_router.route("/<ref>", methods=["DELETE"])
@jwt_required()
def delete_mapping(ref):
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            mongo.db.mapping.delete_one({"ref": ref})
        else:
            mongo.db.mapping.delete_one({"ref": ref, "createdBy": identity})
        return jsonify(successful=f"The ref.: {ref} has been deleted successfully.")
    return {"error": "Unauthorized!"}, 401


@mapping_router.route("/<ref>", methods=["PATCH"])
@jwt_required()
def edit_mapping(ref):
    identity = get_jwt_identity()
    user = getUser(identity)

    if user:
        if 'Admin' in user['roles']:
            mapping_instance = mongo.db.mapping.find_one({"ref": ref}, {"_id": 0})
        else:
            mapping_instance = mongo.db.mapping.find_one({"ref": ref, "createdBy": identity}, {"_id": 0})

        if mapping_instance:
            mapping_instance.update(**request.json)
            mapping_instance = MappingModel(**mapping_instance)
            mongo.db.mapping.update_one({"ref": ref}, {"$set": mapping_instance.dict()})
            return jsonify(successful=f"The ref.: {ref} has been updated successfully.")
        return jsonify(error="The references doesn't exist."), 400
    return {"error": "Unauthorized!"}, 401


@mapping_router.route("/pre/process", methods=["POST"])
@jwt_required()
def pre_process_mapping():
    identity = get_jwt_identity()
    user = getUser(identity)

    if 'ref' in request.json:
        ref = request.json['ref']

        if 'Admin' in user['roles']:
            mapping_instance = mongo.db.mapping.find_one({"ref": ref}, {"_id": 0})
        else:
            mapping_instance = mongo.db.mapping.find_one({"ref": ref, "createdBy": identity}, {"_id": 0})

        if mapping_instance:
            map_classes = {}

            for i in mapping_instance["properties"]:
                for j in mapping_instance["properties"][i]:
                    split = j.split(':')
                    if not split[0] in map_classes:
                        map_classes.update({split[0]: []})
                    map_classes[split[0]].append({"column": i, "property": j})

                    mongo.db.mapping.update_one({"ref": ref, "createdBy": identity},
                                                {"$set": {"pre_process": map_classes}})

            return jsonify(mapping=map_classes)
        return jsonify(succesful=False), 400
    return jsonify(succesful=False), 400
