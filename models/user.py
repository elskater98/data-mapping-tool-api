from pydantic import BaseModel, EmailStr, Field, constr, conlist
import datetime
from typing import Optional


class UserModel(BaseModel):
    username: EmailStr
    password: str
    firstName: Optional[str]
    lastName: Optional[str]
    enable: bool = Field(default=True)
    roles: conlist(str, min_items=1) = Field(default=['User'])
    createdAt: datetime.datetime = Field(default=datetime.datetime.utcnow())

# u = UserModel(**{"username": "francesc@gmail.com", "password": "password"})
# u.json()
