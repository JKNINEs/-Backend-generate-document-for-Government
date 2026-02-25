from pydantic import BaseModel
from typing import Optional

class LoginModel(BaseModel):
    username: str
    password: str


class CreateUserModel(BaseModel):
    username: str
    password: str
    fullname: str
    role: str = "user"  # "user" หรือ "admin"

class UpdateUserModel(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    fullname: Optional[str] = None
    role: Optional[str] = None