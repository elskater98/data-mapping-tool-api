import os

from flask import Blueprint, jsonify
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask import Response

authentication_router = Blueprint('authentication', __name__)


@authentication_router.route('/token', methods=['POST'])
def get_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # TODO: Check Credentials

    if os.getenv('ADMIN_USER') == username and os.getenv('ADMIN_PASSWORD') == password:
        access_token = create_access_token(identity=username, additional_claims={"roles": ["Administrator", "User"]})
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token, sucess=True), 200
    else:
        return Response(jsonify(success=False, error="Username or Password didn't match."), status=400)


@authentication_router.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@authentication_router.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    claims = get_jwt()
    return jsonify(foo=claims)
