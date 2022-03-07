import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.user import UserModel
from utils import getUser

users_router = Blueprint('users', __name__)


@users_router.route("/", methods=["GET"])
@jwt_required()
def get_users():
    identity = get_jwt_identity()
    user = getUser(identity)
    if 'Admin' in user['roles']:
        return jsonify(data=list(mongo.db.users.find({}, {'_id': 0})))
    return jsonify(error=True), 401


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
    return jsonify(error=True, info="The email already exist."), 400


@users_router.route("/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    identity = get_jwt_identity()
    user = getUser(identity)
    if 'Admin' in user['roles'] or identity == id:
        return jsonify(user=mongo.db.users.find_one_or_404({"username": id}, {'_id': 0}))
    return jsonify(error=True), 400


@users_router.route("/<id>", methods=["PATCH"])
@jwt_required()
def edit_user(id):
    identity = get_jwt_identity()
    user = getUser(identity)
    if 'Admin' in user['roles'] or identity == id:
        user.update(**request.json)
        try:
            user_model = UserModel(**user).dict()
            del user_model['password']
            mongo.db.users.update_one({"username": id}, {"$set": user_model})
            return jsonify(successful=f"The user.: {id} has been updated successfully.", user=user_model)
        except Exception as ex:
            return jsonify(error=str(ex)), 400

    return jsonify(error=True), 400


@users_router.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    identity = get_jwt_identity()
    user = getUser(identity)

    if 'Admin' in user['roles'] or identity == id:
        mongo.db.users.delete_one({"username": id})
        return jsonify(successful=f"The user {id} has been deleted successfully.")

    return jsonify(successful=False), 401


@users_router.route("/<id>/change/password", methods=["POST"])
def change_password(id):
    identity = get_jwt_identity()
    user = getUser(identity)
    req = request.json

    hash_code = bcrypt.hashpw(req['password'].encode(), bcrypt.gensalt(10))

    if 'Admin' in user['roles']:
        mongo.db.users.update_one({"username": id}, {"$set": {'password': hash_code}})

    if identity == id:
        if bcrypt.checkpw(req['password'], user['password']):
            if req['newPassword'] == req['confirmPassword']:
                mongo.db.users.update_one({"username": id}, {"$set": {'password': hash_code}})
                return jsonify(), 200

        return jsonify(error="Wrong password!"), 401


@users_router.route("/<id>/reset/password", methods=["POST"])
def reset_password(id):
    # TODO
    pass
