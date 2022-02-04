import datetime

from pydantic import BaseModel, conlist, EmailStr


class InstanceModel(BaseModel):
    ref: str
    name: str
    filenames: conlist(str, min_items=1)
    createdAt: datetime.datetime
    createdBy: EmailStr
