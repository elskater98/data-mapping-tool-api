from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from owlready2 import get_ontology

ontology_router = Blueprint('ontology', __name__)
ontology = get_ontology("BIGG-ontology.owl").load()


@ontology_router.route("/classes", methods=["GET"])
@jwt_required()
def get_classes():
    return jsonify(data=[classe.name for classe in list(ontology.classes())])


@ontology_router.route("/object/properties", methods=["GET"])
@jwt_required()
def get_object_properties():
    return jsonify(data=[classe.name for classe in list(ontology.classes())])
