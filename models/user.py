from pydantic import BaseModel


class UserModel(BaseModel):
    username: str

# u = UserModel(**{"username":"francesc"})
# u.json()
