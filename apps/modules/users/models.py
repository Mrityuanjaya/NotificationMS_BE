from pydantic import BaseModel


class Login(BaseModel):
    access_token: str
    role: int
    token_type: str
