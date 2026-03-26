from pydantic import BaseModel, EmailStr
from typing import Optional


# USER AUTHENTICATION SCHEMAS
class CreateUser(BaseModel):
    username : str
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : str
    username : str
    email : EmailStr