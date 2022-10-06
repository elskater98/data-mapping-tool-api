import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.dataset import DatasetModel
from utils.utils import get_user_by_username, parse_json

cleaning_router = Blueprint('cleaning', __name__)


@cleaning_router.route("/dataset", methods=["POST"])
@jwt_required()
def create_dataset():
    identity = get_jwt_identity()
    body = request.json

    body.update({"createdBy": identity, "createdAt": datetime.datetime.utcnow(), "operations": []})
    try:
        dataset = DatasetModel(**body)
        mongo.db.datasets.insert_one(dataset.dict())
        return jsonify(successful=True, data=parse_json(dataset.dict())), 201
    except Exception as ex:
        return jsonify(error=str(ex)), 400


@cleaning_router.route("/datasets", methods=["GET"])
@jwt_required()
def get_datasets():
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    if user:
        if 'Admin' in user['roles']:
            return jsonify(data=parse_json(list(mongo.db.datasets.find({}))), successful=True)
        else:
            return jsonify(data=parse_json(list(mongo.db.datasets.find({"createdBy": identity}))), successful=True)

    return jsonify(successful=False), 401


@cleaning_router.route("/datasets/<id>/", methods=["GET"])
@jwt_required()
def get_dataset(id):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    if user:
        if 'Admin' in user['roles']:
            data = mongo.db.datasets.find_one({"_id": ObjectId(id)})
        else:
            data = mongo.db.datasets.find({"_id": ObjectId(id), "createdBy": identity})
        return jsonify(data=parse_json(data))

    return jsonify(successful=False), 401
