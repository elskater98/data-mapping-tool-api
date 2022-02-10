import datetime

from pydantic import BaseModel, conlist, EmailStr, Field


class InstanceModel(BaseModel):
    ref: str
    name: str
    filenames: conlist(str, min_items=1)
    createdAt: datetime.datetime
    createdBy: EmailStr
    status: int = Field(default=0)
    mapping: dict = Field(default={})
    classes_to_map: list = Field(default=[])
