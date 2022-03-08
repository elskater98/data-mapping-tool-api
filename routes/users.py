import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from password_strength import PasswordPolicy

from database import mongo
from models.user import UserModel
from utils import getUser

users_router = Blueprint('users', __name__)

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
)


@users_router.route("/", methods=["GET"])
@jwt_required()
def get_users():
    identity = get_jwt_identity()
    current_user = getUser(identity)
    if 'Admin' in current_user['roles']:
        return jsonify(data=list(mongo.db.users.find({}, {'_id': 0})))
    return jsonify(error=True), 401


@users_router.route("/", methods=["POST"])
def create_user():
    body = request.json
    if not mongo.db.users.find_one({"username": body['username']}):
        password_policy = policy.password(body['password'])
        if not password_policy.test():
            hash = bcrypt.hashpw(body['password'].encode(), bcrypt.gensalt(10))
            body.update({'password': hash})
            user = UserModel(**body)
            mongo.db.users.insert_one(user.dict())
            return jsonify(user=user.dict()), 201
        return jsonify(info="Password is not secure.", password_strength=password_policy.strength(),
                       password_requirements=str(password_policy.test())), 400
    return jsonify(error=True, info="The email already exist."), 400


@users_router.route("/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    identity = get_jwt_identity()
    current_user = getUser(identity)
    if 'Admin' in current_user['roles'] or identity == id:
        return jsonify(user=mongo.db.users.find_one_or_404({"username": id}, {'_id': 0}))
    return jsonify(error=True), 400


@users_router.route("/<id>", methods=["PATCH"])
@jwt_required()
def edit_user(id):
    identity = get_jwt_identity()
    current_user = getUser(identity)
    user = getUser(id)
    if 'Admin' in current_user['roles'] or identity == id:
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
@jwt_required()
def change_password(id):
    identity = get_jwt_identity()
    current_user = getUser(identity)
    user = getUser(id)

    req = request.json

    hash_code = bcrypt.hashpw(req['newPassword'].encode(), bcrypt.gensalt(10)).decode()

    if 'currentPassword' in req and 'newPassword' in req and 'confirmPassword' in req:
        if 'Admin' in current_user['roles']:
            mongo.db.users.update_one({"username": id}, {"$set": {'password': hash_code}})
            return jsonify(info="Password changed.")

        if identity == id:
            if bcrypt.checkpw(req['currentPassword'].encode(), user['password'].encode()):
                if req['newPassword'] == req['confirmPassword']:
                    password_policy = policy.password(req['newPassword'])
                    if not password_policy.test():
                        mongo.db.users.update_one({"username": id}, {"$set": {'password': hash_code}})
                        return jsonify(info="Password changed.")
                    return jsonify(error="Password is not secure.", password_strength=password_policy.strength(),
                                   password_requirements=str(password_policy.test())), 400
            return jsonify(error="New password and confirm password didn't match!"), 400
        return jsonify(error="Wrong current password!"), 401
    return jsonify(error="Bad Request"), 400


@users_router.route("/<id>/reset/password", methods=["POST"])
@jwt_required()
def reset_password(id):
    # TODO
    pass
