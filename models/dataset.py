import datetime

from pydantic import BaseModel, EmailStr


class DatasetModel(BaseModel):
    name: str
    file_id: str
    createdAt: datetime.datetime
    createdBy: EmailStr
    operations: list
