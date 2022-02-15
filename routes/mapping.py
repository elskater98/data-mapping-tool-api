from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

mapping_router = Blueprint('mapping', __name__)


@mapping_router.route("/", methods=["GET"])
@jwt_required()
def generate_mapping_config():
    jsonify(successful=True)
