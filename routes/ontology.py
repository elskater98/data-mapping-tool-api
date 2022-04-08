import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import mongo
from models.ontology import OntologyModel, VisibilityEnum
from utils import get_user_by_username, parse_json, remove_file, get_file, define_ontology

ontology_router = Blueprint('ontology', __name__)


@ontology_router.route("/<id>/classes", methods=["GET"])
@jwt_required()
def get_classes(id):
    ontology = define_ontology(id)
    return jsonify(data=[{"label": str(i), "value": str(i)} for i in list(ontology.classes())])


@ontology_router.route("/<id>/relations", methods=["GET"])
@jwt_required()
def get_classes_relations(id):
    ontology = define_ontology(id)
    relations = [{"class": str(i), "relations": list(i._get_class_possible_relations()).__str__()[1:-1].split(',')} for
                 i in list(ontology.classes())]
    return jsonify(data=relations)


@ontology_router.route("/<id>/properties/<property_type>", methods=["GET"])
@jwt_required()
def get_object_properties(id, property_type):
    ontology = define_ontology(id)
    properties = []

    if property_type == 'data':
        properties = list(ontology.data_properties())

    if property_type == 'object':
        properties = list(ontology.object_properties())

    if property_type == 'annotation':
        properties = list(ontology.annotation_properties())

    if property_type == 'all':
        properties = list(ontology.properties())

    if 'classes' in request.args:
        classes = request.args['classes'].split(',')
        properties = [elem for elem in properties if str(elem.domain)[1:-1] in classes]

    return jsonify(
        data=[
            {"name": i.name,
             "value": str(i.domain)[1:-1] + ':' + i.name,
             "range": str(i.range)[1:-1],
             "domain": str(i.domain)[1:-1]} for i in properties])


@ontology_router.route("/<id>/classes/relations", methods=["POST"])
@jwt_required()
def get_relations(id):
    req = request.json
    relations = {}
    ontology = define_ontology(id)

    for i in ontology.object_properties():
        if i.domain and i.range:
            if str(i.domain[0]) in req['classes'] and str(i.range[0]) in req['classes']:
                rel = {"from": str(i.domain[0]), "to": str(i.range[0]), "relation": str(i)}
                relations.update({str(i): rel})

    return jsonify(successful=True, relations=relations)


@ontology_router.route("/<id>/view", methods=["GET"])
def get_ontology_view(id):
    ontology = define_ontology(id)
    classes = [{'id': str(_class), 'data': {'label': str(_class)}, 'position': {'x': 0, 'y': 0}} for _class in
               ontology.classes()]

    relations = [
        {"source": str(i.domain[0]), "target": str(i.range[0]), "id": str(i), "label": str(i), 'type': 'smooth',
         'style': {'stroke': 'black'}, 'arrowHeadType': 'arrowclosed', 'animated': True} for i in
        ontology.object_properties()]

    return jsonify(classes=classes, relations=relations)


@ontology_router.route("/<ontology>", methods=["POST"])
@jwt_required()
def create_ontology(ontology):
    identity = get_jwt_identity()

    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify(error="No file attached."), 400

    file = request.files['file']
    file_id = mongo.save_file(filename=file.filename, fileobj=file, kwargs={"owner": identity})

    ontology_model = OntologyModel(filename=file.filename, file_id=str(file_id), ontology_name=ontology,
                                   createdBy=identity, createdAt=datetime.datetime.utcnow(),
                                   visibility=VisibilityEnum.private)

    mongo.db.ontologies.insert_one(ontology_model.dict())

    return jsonify(successful=True)


@ontology_router.route("/", methods=["GET"])
@jwt_required()
def get_ontologies():
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {} if 'Admin' in user['roles'] else {
        "$or": [{"visibility": VisibilityEnum.public}, {"createdBy": identity}]}
    ontologies = mongo.db.ontologies.find(query)

    return jsonify(data=parse_json(ontologies))


@ontology_router.route("/<id>", methods=["GET"])
@jwt_required()
def get_ontology(id):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {"_id": ObjectId(id)} if 'Admin' in user['roles'] else {
        "$or": [{"visibility": VisibilityEnum.public}, {"createdBy": identity}]}
    ontologies = mongo.db.ontologies.find_one(query)

    return jsonify(data=parse_json(ontologies))


@ontology_router.route("/<id>", methods=['PATCH'])
@jwt_required()
def edit_ontology(id):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    if user:
        query = {"_id": ObjectId(id)} if 'Admin' in user['roles'] else {"_id": ObjectId(id),
                                                                        "createdBy": identity}
        ontology_instance = mongo.db.ontologies.find_one(query, {"_id": 0})

        if ontology_instance:
            ontology_instance.update(**request.json)
            try:
                ontology = OntologyModel(**ontology_instance)
                mongo.db.ontologies.update_one({"_id": ObjectId(id)}, {"$set": ontology.dict()})
                return jsonify(successful=f"The ref.: {id} has been updated successfully.", instance=ontology.dict())
            except Exception as ex:
                return jsonify(error=str(ex)), 400
        return jsonify(successful=False, error="The references doesn't exist."), 400
    return jsonify(successful=False), 401


@ontology_router.route("/<id>", methods=["DELETE"])
@jwt_required()
def remove_ontology(id):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {"_id": ObjectId(id)} if 'Admin' in user['roles'] else {"_id": ObjectId(id),
                                                                    "createdBy": identity}
    ontology_instance = mongo.db.ontologies.find_one(query)

    if ontology_instance:
        remove_file(ontology_instance['file_id'])
        mongo.db.ontologies.delete_one({"_id": ObjectId(id)})
        return jsonify()

    return jsonify(), 400


@ontology_router.route("/<id>/download", methods=["GET"])
@jwt_required()
def download_ontology(id):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {"_id": ObjectId(id)} if 'Admin' in user['roles'] else {
        "$or": [{"_id": ObjectId(id), "visibility": VisibilityEnum.public},
                {"_id": ObjectId(id), "createdBy": identity}]}

    ontology_instance = mongo.db.ontologies.find_one(query)

    if ontology_instance:
        return jsonify(data=get_file(ontology_instance['file_id']).getvalue())

    return jsonify(error="No access to file"), 401
