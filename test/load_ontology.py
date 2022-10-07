from owlready2 import *

if __name__ == '__main__':
    path_file = f"file:///Users/francesc/Desktop/data-mapping-tool-api/output/kjbadfguoad.owl"
    ontology = get_ontology(path_file, base_iri='ss').load()
    print(list(ontology.classes()))
