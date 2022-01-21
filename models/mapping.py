import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, conlist, Field, EmailStr


class MappingModel(BaseModel):
    ref: str
    rawColumns: conlist(str, min_items=1)
    selectedColumns: conlist(str, min_items=1)
    filename: str
    createdAt: datetime.datetime = Field(default=datetime.datetime.utcnow())
    lastModificationAt: Optional[datetime.datetime]
    createdBy: EmailStr
    finished: bool = Field(default=False)
