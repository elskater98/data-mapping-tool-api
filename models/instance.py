import datetime

from pydantic import BaseModel, conlist, EmailStr, Field, constr


class InstanceModel(BaseModel):
    ref: str
    name: str
    description: constr(max_length=280)
    filenames: conlist(str, min_items=1)
    createdAt: datetime.datetime
    createdBy: EmailStr
    status: int = Field(default=0)
    mapping: dict = Field(default={})
    classes_to_map: list = Field(default=[])
