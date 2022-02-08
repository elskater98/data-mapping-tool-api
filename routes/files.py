import os

from flask import Blueprint, request, jsonify
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flask import send_from_directory
from utils import allowed_files
import pandas as pd

files_router = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = ['json', 'csv']


@files_router.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return {"error": "No file attached."}, 400

    file = request.files['file']

    if file and allowed_files(filename=file.filename, allowed_extensions=ALLOWED_EXTENSIONS):
        identity = get_jwt_identity()

        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], identity + '/' + filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        return {"successful": True}

    return {"error": "No file attached."}, 400


@files_router.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_file(filename):
    identity = get_jwt_identity()
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], identity + '/'), filename)


@files_router.route("/<filename>", methods=["GET"])
@jwt_required()
def get_columns(filename):
    identity = get_jwt_identity()
    df = pd.read_csv(f"{current_app.config['UPLOAD_FOLDER']}/{identity}/{filename}")
    return jsonify(data={"columns": list(df.columns), "sample": df.head(25).to_dict(orient="records")})
