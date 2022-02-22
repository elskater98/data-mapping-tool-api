# The aim of this fragment of code is generate the patterns that allow us to build a yarrrml file.
# To do it I follow the structures from https://rml.io/yarrrml/.

PREFIXES = {"dbo": "https://dbpedia.org/ontology/", "bigg": "https://bigg-project.eu/ontology#"}


def add_prefixes(prefixes=None):
    if prefixes is None:
        prefixes = PREFIXES

    string = "prefixes:\n"
    for key, value in prefixes.items():
        string += f"  {key}: {value}\n"

    return string + "\n"


def init_mappings():
    return "mappings:\n"


def add_mapping(mapping_name: str):
    return f"  {mapping_name}:\n"


def init_sources():
    return "    sources:\n"


def add_source(source: str, delimiter='.'):
    source_extension = source.split(delimiter)[-1]
    return f"      - [ '{source}~{source_extension}' ]\n"


def add_simple_subject(subject_name: str, column_name: str):
    return f"    s: {subject_name}/$({column_name})\n"


def init_predicate_object():
    return "    po:\n"


def add_predicate_object_simple(predicate: str, _object: str):
    return f"      - [ {predicate}, {_object} ]\n"


def add_predicate_object_datatype(predicate: str, _object: str, datatype: str):
    return f"""
          - p: {predicate}
            o:
              - value: {_object}
                datatype: {datatype}
            """


def add_predicade_object_datatype_language(lang: str):
    return f"         language: {lang}"


def link_entities(relation: str, mapping_name: str, function: str, key1: str, key2: str):
    return f"      - p: {relation}\n        o:\n          mapping: {mapping_name}\n" \
           f"          condition:\n            function: {function}\n            parameters:\n" \
           f"              - [ str1, {key1} ]\n              - [ str2, {key2} ]\n\n"


if __name__ == '__main__':
    s = ""
    s += add_prefixes()

    s += init_mappings()

    s += add_mapping("building")
    s += init_sources()
    s += add_source("building.csv")
    s += add_simple_subject("BIGG-ontology.Building", "Num. Ens")

    s += init_predicate_object()
    s += add_predicate_object_simple("a", "schema:BIGG-ontology.Building")
    s += add_predicate_object_simple("schema:buildingID", "$(Num. Ens)")
    s += add_predicate_object_simple("schema:buildingIDFromOrganization", "$(Num. Ens)")
    s += add_predicate_object_simple("schema:buildingName", "$(Espai)")
    s += add_predicate_object_simple("schema:buildingUseType", "$(Tipus d'ús)")

    with open("../yarrrml-example/building-auto.yml", 'w') as file:
        file.write(s)
