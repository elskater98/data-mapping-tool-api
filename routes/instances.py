import datetime
import uuid

import pymongo
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.instance import InstanceModel
from utils.utils import get_user_by_username, define_ontology

instances_router = Blueprint('instances', __name__)


@instances_router.route("/", methods=["GET"])
@jwt_required()
def get_instances():
    identity = get_jwt_identity()
    user = get_user_by_username(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(successful=True,
                           data=list(mongo.db.instances.find({}, {"_id": 0}).sort([("createdAt", pymongo.DESCENDING)])))
        else:
            return jsonify(successful=True,
                           data=list(mongo.db.instances.find({"createdBy": user['username']}, {"_id": 0}).sort(
                               [("createdAt", pymongo.DESCENDING)])))

    return jsonify(successful=False), 401


@instances_router.route("/<ref>", methods=["GET"])
@jwt_required()
def get_instance(ref):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)
    if user:
        if 'Admin' in user['roles']:
            return jsonify(successful=True, data=mongo.db.instances.find_one({"ref": ref}, {"_id": 0}))
        else:
            return jsonify(successful=True,
                           data=mongo.db.instances.find_one({"ref": ref, "createdBy": identity}, {"_id": 0}))
    return jsonify(successful=False), 401


@instances_router.route("/", methods=["POST"])
@jwt_required()
def create_instance():
    identity = get_jwt_identity()
    body = request.json
    body.update({"createdBy": identity, "ref": str(uuid.uuid4()), "createdAt": datetime.datetime.utcnow()})
    try:
        instance = InstanceModel(**body)
        mongo.db.instances.insert_one(instance.dict())
        return jsonify(successful=True, instance=instance.dict()), 201
    except Exception as ex:
        return jsonify(error=str(ex)), 400


@instances_router.route("/<ref>", methods=["PATCH"])
@jwt_required()
def edit_instance(ref):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    if user:
        query = {"ref": ref} if 'Admin' in user['roles'] else {"ref": ref, "createdBy": identity}
        instance = mongo.db.instances.find_one(query, {"_id": 0})

        if instance:
            instance.update(**request.json)
            try:
                instance = InstanceModel(**instance)
                mongo.db.instances.update_one({"ref": ref}, {"$set": instance.dict()})
                return jsonify(successful=f"The ref.: {ref} has been updated successfully.", instance=instance.dict())
            except Exception as ex:
                return jsonify(error=str(ex)), 400
        return jsonify(successful=False, error="The references doesn't exist."), 400
    return jsonify(successful=False), 401


@instances_router.route("/<ref>", methods=["DELETE"])
@jwt_required()
def delete_instance(ref):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)
    if user:
        query = {"ref": ref} if 'Admin' in user['roles'] else {"ref": ref, "createdBy": identity}
        instance = mongo.db.instances.find_one(query)
        for filename in instance['filenames']:
            del_query = {"kwargs.owner": instance['createdBy'], 'filename': filename}
            file = mongo.db.fs.files.find_one(del_query)
            mongo.db.fs.chunks.delete_many({"files_id": file['_id']})
            mongo.db.fs.files.delete_one(del_query)

        mongo.db.instances.delete_one(query)
        return jsonify(successful=f"The ref.: {ref} has been deleted successfully.")
    return jsonify(successful=False), 401


@instances_router.route("/<ref>/initialize/schema", methods=["POST"])
@jwt_required()
def init_instance_ontology(ref):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {'ref': ref} if 'Admin' in user['roles'] else {'ref': ref, "createdBy": identity}
    instance = mongo.db.instances.find_one(query, {"_id": 0})

    ontology = define_ontology(instance['current_ontology'])

    if instance:
        classes = [str(i) for i in list(ontology.classes())]
        relations = ontology.object_properties()

        for _class in classes:
            if 'mapping' not in instance:
                instance.update({"mapping": {}})
            instance['mapping'].update(
                {_class: {"status": False, "fileSelected": instance['filenames'][0], "columns": {}}})

        for relation in relations:
            if 'relations' not in instance:
                instance.update({"relations": {}})

            if relation.domain and relation.range:
                instance['relations'].update(
                    {str(relation): {"from": str(relation.domain[0]), "to": str(relation.range[0]),
                                     "relation": str(relation),
                                     "selected": False, "from_rel": None, "to_rel": None}})

        try:
            instance_model = InstanceModel(**instance)
            mongo.db.instances.update_one(query, {
                "$set": {"mapping": instance['mapping'], "relations": instance['relations']}})
            return jsonify(successful=True, instance=instance_model.dict())
        except Exception as ex:
            return jsonify(successful=False, error=str(ex)), 400

    return jsonify(successful=False), 401
