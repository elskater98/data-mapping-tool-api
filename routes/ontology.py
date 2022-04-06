import datetime
import io
import os

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from owlready2 import default_world, World, get_ontology

from database import mongo
from models.instance import InstanceModel
from models.ontology import OntologyModel, VisibilityEnum
from utils import get_user_by_username

ontology_router = Blueprint('ontology', __name__)
ontology = get_ontology(os.getenv("ONTOLOGY_PATH", os.path.join(os.path.abspath(os.getcwd()), "ontology.owl"))).load()


@ontology_router.route("/query", methods=["POST"])
@jwt_required()
def sparql_query():
    data = list(default_world.sparql(request.json['query']))
    return jsonify(data=data.__str__())


@ontology_router.route("/classes", methods=["GET"])
@jwt_required()
def get_classes():
    return jsonify(data=[{"label": str(i), "value": str(i)} for i in list(ontology.classes())])


@ontology_router.route("/relations", methods=["GET"])
@jwt_required()
def get_classes_relations():
    relations = [{"class": str(i), "relations": list(i._get_class_possible_relations()).__str__()[1:-1].split(',')} for
                 i in list(ontology.classes())]
    return jsonify(data=relations)


@ontology_router.route("/properties/<property_type>", methods=["GET"])
@jwt_required()
def get_object_properties(property_type):
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


@ontology_router.route("/classes/relations", methods=["POST"])
@jwt_required()
def get_relations():
    req = request.json
    relations = {}
    for i in ontology.object_properties():
        if str(i.domain[0]) in req['classes'] and str(i.range[0]) in req['classes']:
            rel = {"from": str(i.domain[0]), "to": str(i.range[0]), "relation": str(i)}
            relations.update({str(i): rel})

    return jsonify(successful=True, relations=relations)


@ontology_router.route("/", methods=["GET"])
def get_ontology_view():
    classes = [{'id': str(_class), 'data': {'label': str(_class)}, 'position': {'x': 0, 'y': 0}} for _class in
               ontology.classes()]

    relations = [
        {"source": str(i.domain[0]), "target": str(i.range[0]), "id": str(i), "label": str(i), 'type': 'smooth',
         'style': {'stroke': 'black'}, 'arrowHeadType': 'arrowclosed', 'animated': True} for i in
        ontology.object_properties()]

    return jsonify(classes=classes, relations=relations)


@ontology_router.route("/init/instance/<ref>", methods=["POST"])
@jwt_required()
def init_instance_ontology(ref):
    identity = get_jwt_identity()
    user = get_user_by_username(identity)

    query = {'ref': ref} if 'Admin' in user['roles'] else {'ref': ref, "createdBy": identity}
    instance = mongo.db.instances.find_one(query, {"_id": 0})
    if instance:
        classes = [str(i) for i in list(ontology.classes())]
        relations = ontology.object_properties()

        for _class in classes:
            if 'mapping' not in instance:
                instance.update({"mapping": {}})
            instance['mapping'].update(
                {_class: {"status": False, "fileSelected": instance['filenames'][0], "columns": {}}})

        for relation in relations:
            if 'relations' not in instance:
                instance.update({"relations": {}})
            instance['relations'].update(
                {str(relation): {"from": str(relation.domain[0]), "to": str(relation.range[0]),
                                 "relation": str(relation),
                                 "selected": False, "from_rel": None, "to_rel": None}})

        try:
            instance_model = InstanceModel(**instance)
            mongo.db.instances.update_one(query, {
                "$set": {"mapping": instance['mapping'], "relations": instance['relations']}})
            return jsonify(successful=True, instance=instance_model.dict())
        except Exception as ex:
            return jsonify(successful=False, error=str(ex)), 400

    return jsonify(successful=False), 401


@ontology_router.route("/upload/<ontology>", methods=["POST"])
@jwt_required()
def upload_ontology(ontology):
    identity = get_jwt_identity()

    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify(error="No file attached."), 400

    file = request.files['file']
    file_id = mongo.save_file(filename=file.filename, fileobj=file)

    ontology_model = OntologyModel(filename=file.filename, file_id=str(file_id), ontology_name=ontology,
                                   createdBy=identity, createdAt=datetime.datetime.utcnow(),
                                   visibility=VisibilityEnum.private)

    mongo.db.ontologies.insert_one(ontology_model.dict())

    return jsonify(successful=True)


@ontology_router.route("")
@jwt_required()
def get_ontologies():
    pass


@ontology_router.route("<ontology>")
@jwt_required()
def get_ontology(ontology):
    pass


@ontology_router.route("<ontology>")
@jwt_required()
def edit_ontology():
    pass


@ontology_router.route("<ontology>")
@jwt_required()
def remove_ontology():
    pass


def define_ontology(ontology_id):
    # https://owlready2.readthedocs.io/en/latest/world.html

    ontology_record = mongo.db.ontologies.find_one({"_id": ObjectId(ontology_id)})
    ontology_file = recover_file(ontology_record['file_id'])
    ontology = World()
    io.StringIO("sss")
    # return ontology.get_ontology().load()


def recover_file(file_id):
    pass
