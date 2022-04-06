import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class VisibilityEnum(str, Enum):
    public = 'public'
    private = 'private'


class OntologyModel(BaseModel):
    filename: str
    file_id: str
    description: Optional[str]
    ontology_name: str
    createdAt: datetime.datetime
    createdBy: EmailStr
    visibility: VisibilityEnum
