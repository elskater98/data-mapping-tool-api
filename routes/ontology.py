from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from owlready2 import get_ontology, default_world

ontology_router = Blueprint('ontology', __name__)
ontology = get_ontology("BIGG-ontology.owl").load()


@ontology_router.route("/query", methods=["POST"])
@jwt_required()
def sparql_query():
    data = list(default_world.sparql(request.json['query']))
    return jsonify(data=data.__str__())


@ontology_router.route("/classes", methods=["GET"])
@jwt_required()
def get_classes():
    return jsonify(data=[{"label": str(i), "value": str(i)} for i in list(ontology.classes())])


@ontology_router.route("/classes/relations", methods=["GET"])
@jwt_required()
def get_classes_relations():
    relations = []
    for i in list(ontology.classes()):
        relations.append(
            {"class": str(i), "relations": list(i._get_class_possible_relations()).__str__()[1:-1].split(',')})
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

    return jsonify(
        data=[
            {"name": i.name,
             "value": str(i.domain)[1:-1] + ':' + i.name,
             "range": str(i.range)[1:-1],
             "domain": str(i.domain)[1:-1]} for i in properties])
