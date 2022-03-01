import os
from io import StringIO

import pandas as pd
from flask import Blueprint, request, jsonify
from flask import current_app
from flask import send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from utils import allowed_files

files_router = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = ['csv']


@files_router.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify(error="No file attached."), 400

    file = request.files['file']

    if file and allowed_files(filename=file.filename, allowed_extensions=ALLOWED_EXTENSIONS):
        identity = get_jwt_identity()
        mongo.save_file(filename=file.filename, fileobj=file, kwargs={"owner": identity})

        return jsonify(successful=True)

    return jsonify(error="No file attached."), 400


@files_router.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_file(filename):
    identity = get_jwt_identity()
    has_access = mongo.db.fs.files.find_one({"kwargs.owner": identity, "filename": filename})
    if has_access:
        return mongo.send_file(filename=filename)
    return jsonify(error="No access to file"), 401


@files_router.route("/<filename>", methods=["GET"])
@jwt_required()
def get_columns(filename):
    identity = get_jwt_identity()

    has_access = mongo.db.fs.files.find_one({"kwargs.owner": identity, "filename": filename})
    if has_access:
        x = mongo.send_file(filename=filename)
        x = x.response.file.read().decode('utf-8')
        df = pd.read_csv(StringIO(x), sep=',')
        return jsonify(columns=list(df.columns), sample=df.head(25).to_dict(orient="records"))
    return jsonify(error="No access to file"), 401
