from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from utils import getUser

PREFIXES = """
prefixes:
  ex: http://www.example.com/
  e: http://myontology.com/
  dbo: http://dbpedia.org/ontology/
  grel: http://users.ugent.be/~bjdmeest/function/grel.ttl#

"""

mapping_router = Blueprint('mapping', __name__)


@mapping_router.route("/", methods=["POST"])
@jwt_required()
def generate_mapping_config():
    identity = get_jwt_identity()
    user = getUser(identity)
    req = request.json

    if 'ref' in req.keys() and 'class' in req.keys() and 'type' in req.keys():
        query = {'ref': req['ref']} if 'Admin' in user['roles'] else {'ref': req['ref'], "createdBy": identity}
        instance = mongo.db.instances.find_one(query, {"_id": 0})
        filename = instance['mapping'][req['class']]['fileSelected']
        yaml_file = PREFIXES
        print(yaml_file)

        return jsonify(successful=True, yaml=yaml_file)

    return jsonify(successful=False), 400
