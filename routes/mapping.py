import json
import os.path
import uuid

import pandas as pd
from bson import ObjectId
from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.mapping import MappingModel

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
    body.update({"createdBy": identity, "ref": str(uuid.uuid4())})
    mapping = MappingModel(**body)
    mongo.db.mapping.insert_one(mapping.dict())
    return jsonify(data=mapping.dict()), 201
