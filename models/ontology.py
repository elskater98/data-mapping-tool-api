from pydantic import BaseModel, Field


class OntologyModel(BaseModel):
    filename: str
    file_id: str
    ontology_name: str
    selected: bool = Field(default=True)
