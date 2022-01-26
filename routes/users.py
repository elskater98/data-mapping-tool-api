import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from database import mongo
from models.user import UserModel

users_router = Blueprint('users', __name__)


@users_router.route("/", methods=["GET"])
@jwt_required()
def get_users():
    return jsonify(data=list(mongo.db.users.find({}, {'_id': 0})))


@users_router.route("/", methods=["POST"])
@jwt_required()
def create_user():
    body = request.json
    if not mongo.db.users.find_one({"username": body['username']}):
        hash = bcrypt.hashpw(body['password'].encode(), bcrypt.gensalt(10))
        body.update({'password': hash})
        user = UserModel(**body)
        mongo.db.users.insert_one(user.dict())
        return user.json(), 201
    return {"error": "The email already exist."}, 400


@users_router.route("/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    return mongo.db.users.find_one_or_404({"username": id}, {'_id': 0})


@users_router.route("/<id>", methods=["PATCH"])
@jwt_required()
def edit_user(id):
    # TODO
    pass


@users_router.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    # TODO
    pass


@users_router.route("/<id>/reset/password", methods=["POST"])
def reset_password(id):
    # TODO
    pass
