from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from owlready2 import get_ontology

ontology_router = Blueprint('ontology', __name__)
ontology = get_ontology("BIGG-ontology.owl").load()


@ontology_router.route("/classes", methods=["GET"])
@jwt_required()
def get_classes():
    return jsonify(data=[classe.name for classe in list(ontology.classes())])


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
        data=[{"name": property.name, "range": str(property.range)[1:-1],
               "domain": str(property.domain)[1:-1]} for property in properties])
