import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, conlist


class UserModel(BaseModel):
    username: EmailStr
    password: str
    firstName: Optional[str]
    lastName: Optional[str]
    enable: bool = Field(default=True)
    roles: conlist(str, min_items=1) = Field(default=['User'])
    createdAt: datetime.datetime = Field(default=datetime.datetime.utcnow())
