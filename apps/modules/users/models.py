from pydantic import BaseModel
from pydantic import EmailStr


class LoginEmail(BaseModel):
    email: EmailStr


class Login(BaseModel):
    access_token: str
    role: int
    token_type: str
