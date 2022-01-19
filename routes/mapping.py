import os.path

from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

mapping_router = Blueprint('mapping', __name__)


@mapping_router.route("/data/sample", methods=["GET"])
@jwt_required()
def data_sample():
    identity = get_jwt_identity()
    if request.args.get('filename'):
        filename = request.args.get('filename')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], identity + '/' + filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            return jsonify(data=df.to_dict(orient="records"))
        return {"error": f"The file '{filename}' don't exist."}, 400
    return {"error": "Field 'filename' not found."}, 400
