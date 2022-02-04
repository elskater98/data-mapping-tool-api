import datetime
import uuid

import pymongo
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.instance import InstanceModel
from utils import getUser

instances_router = Blueprint('instances', __name__)


@instances_router.route("/", methods=["GET"])
@jwt_required()
def get_instances():
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(
                data=list(mongo.db.instances.find({}, {"_id": 0}).sort([("createdAt", pymongo.DESCENDING)])))
        else:
            return jsonify(data=list(mongo.db.instances.find({"createdBy": user['username']}, {"_id": 0}).sort(
                [("createdAt", pymongo.DESCENDING)])))

    return {"error": "Unauthorized!"}, 401


@instances_router.route("/<ref>", methods=["GET"])
@jwt_required()
def get_instance(ref):
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(data=mongo.db.instances.find_one({"ref": ref}, {"_id": 0}))
        else:
            return jsonify(data=mongo.db.instances.find_one({"ref": ref, "createdBy": identity}, {"_id": 0}))
    return {"error": "Unauthorized!"}, 401


@instances_router.route("/", methods=["POST"])
@jwt_required()
def create_instance():
    identity = get_jwt_identity()
    body = request.json
    body.update({"createdBy": identity, "ref": str(uuid.uuid4()), "createdAt": datetime.datetime.utcnow()})
    try:
        mapping = InstanceModel(**body)
        mongo.db.instances.insert_one(mapping.dict())
        return jsonify(data=mapping.dict()), 201
    except Exception as ex:
        return jsonify(error=str(ex)), 400


@instances_router.route("/<ref>", methods=["PATCH"])
@jwt_required()
def edit_instance(ref):
    identity = get_jwt_identity()
    user = getUser(identity)

    if user:
        if 'Admin' in user['roles']:
            instance = mongo.db.instances.find_one({"ref": ref}, {"_id": 0})
        else:
            instance = mongo.db.instances.find_one({"ref": ref, "createdBy": identity}, {"_id": 0})

        if instance:
            instance.update(**request.json)
            try:
                instance = InstanceModel(**instance)
                mongo.db.instances.update_one({"ref": ref}, {"$set": instance.dict()})
                return jsonify(successful=f"The ref.: {ref} has been updated successfully.")
            except Exception as ex:
                return jsonify(error=str(ex)), 400
        return jsonify(error="The references doesn't exist."), 400
    return {"error": "Unauthorized!"}, 401


@instances_router.route("/<ref>", methods=["DELETE"])
@jwt_required()
def delete_instance(ref):
    identity = get_jwt_identity()
    user = getUser(identity)
    if user:
        if 'Admin' in user['roles']:
            mongo.db.instances.delete_one({"ref": ref})
        else:
            mongo.db.instances.delete_one({"ref": ref, "createdBy": identity})
        return jsonify(successful=f"The ref.: {ref} has been deleted successfully.")
    return {"error": "Unauthorized!"}, 401
